""" Module implementing robotic sensors: Cameras, Lidar, touch sensing.

These sensors are very close to physical sensors that could be used on real robots.
These sensors can be noisy.
Importantly, as Simple-Playgrounds is a 2D environments, these sensors are 1D.
"""
import math
from typing import List, Optional, Dict, Union

import numpy as np
import pymunk
from PIL import Image, ImageDraw, ImageFont
from skimage.transform import resize

from .sensor import RayCollisionSensor, SensorDevice
from ..parts.parts import Part
from ...common.definitions import SensorTypes
from ...common.entity import Entity
from ...configs.parser import parse_configuration

# pylint: disable=no-member


class RgbCamera(RayCollisionSensor):
    """
    Provides a 1D image (line of RGB pixels) from the point of view of the anchor.
    """

    sensor_type = SensorTypes.RGB

    def __init__(self,
                 anchor: Part,
                 invisible_elements: Optional[Union[List[Entity],
                                                    Entity]] = None,
                 normalize: bool = True,
                 noise_params: Optional[Dict] = None,
                 **kwargs):

        default_config = parse_configuration('agent_sensors', self.sensor_type)
        kwargs = {**default_config, **kwargs}

        super().__init__(anchor=anchor,
                         invisible_elements=invisible_elements,
                         normalize=normalize,
                         noise_params=noise_params,
                         remove_duplicates=False,
                         **kwargs)

        self._sensor_max_value = 255

    def _compute_raw_sensor(self, playground, *_):

        collision_points = self._compute_points(playground)

        pixels = np.zeros((self._resolution, 3))

        for angle_index, ray_angle in enumerate(self._ray_angles):

            collision = collision_points[ray_angle]

            if collision:

                elem_colliding = playground.get_entity_from_shape(
                    pm_shape=collision.shape)

                if collision.alpha == 0.0:

                    angle = self._anchor.pm_body.angle + ray_angle
                    collision_pt = self._anchor.position + pymunk.Vec2d(
                        self._min_range + 1, 0).rotated(angle)

                else:
                    collision_pt = collision.point

                rel_pos_point = (
                    collision_pt -
                    elem_colliding.position).rotated(math.pi / 2 -
                                                     elem_colliding.angle)

                rgb = elem_colliding.get_pixel(rel_pos_point)

                pixels[angle_index] = rgb

        pixels = pixels[:, ::-1]

        self.sensor_values = pixels

    def _apply_normalization(self):
        self.sensor_values /= 255.

    def _get_null_sensor(self):
        return np.zeros(self.shape)

    @property
    def shape(self):
        return self._resolution, 3

    def draw(self, width, height):
        """
        Function that creates an image for visualizing a sensor.

        Args:
            width: width of the image
            height: height of the rendered 1D sensor

        Returns:
            Numpy array containing the visualization of the sensor values.
        """

        img = np.expand_dims(self.sensor_values, 0)
        img = resize(img, (height, width), order=0, preserve_range=True)
        if not self._normalize:
            img /= 255.

        return img


class GreyCamera(RgbCamera):
    """
    Provides a 1D image (line of Grey-level pixels) from the point of view of the anchor.
    """

    sensor_type = SensorTypes.GREY

    def _compute_raw_sensor(self, playground, *_):
        super()._compute_raw_sensor(playground)
        self.sensor_values = np.dot(self.sensor_values[..., :3],
                                    [0.114, 0.299, 0.587]).reshape(self.shape)

    @property
    def shape(self):
        return self._resolution, 1

    def draw(self, width, height):
        img = np.repeat(self.sensor_values, 3, axis=1)
        img = np.expand_dims(img, 0)
        img = resize(img, (height, width, 3), order=0, preserve_range=True)

        if not self._normalize:
            img /= 255.

        return img


class BlindCamera(GreyCamera):
    def _compute_raw_sensor(self, playground, *_):
        self.sensor_values = np.zeros(self.shape)


class Lidar(RayCollisionSensor):
    """
    Lidar are Sensors that measure distances by projecting rays.
    """

    sensor_type = SensorTypes.LIDAR

    def __init__(self,
                 anchor: Part,
                 invisible_elements: Optional[Union[List[Entity],
                                                    Entity]] = None,
                 normalize: bool = True,
                 noise_params: Optional[Dict] = None,
                 **kwargs):

        default_config = parse_configuration('agent_sensors', self.sensor_type)
        kwargs = {**default_config, **kwargs}

        super().__init__(anchor=anchor,
                         invisible_elements=invisible_elements,
                         normalize=normalize,
                         noise_params=noise_params,
                         remove_duplicates=False,
                         remove_occluded=False,
                         **kwargs)

        self._sensor_max_value = self._max_range

    def _compute_raw_sensor(self, playground, *_):

        collision_points = self._compute_points(playground)

        pixels = np.ones(self._resolution) * self._max_range

        for angle_index, ray_angle in enumerate(self._ray_angles):

            collision = collision_points[ray_angle]

            if collision:
                pixels[angle_index] = collision.alpha * (self._max_range - self._min_range - 1) + self._min_range + 1

        self.sensor_values = pixels[:].astype(float).reshape(self.shape)

    def _get_null_sensor(self):
        return np.zeros(self.shape)

    @property
    def shape(self):
        return self._resolution, 1

    def _apply_normalization(self):

        self.sensor_values /= self._sensor_max_value

    def draw(self, width, height):

        img = np.repeat(self.sensor_values, 3, axis=1)
        img = np.expand_dims(img, 0)
        img = resize(img, (height, width, 3), order=0, preserve_range=True)

        if not self._normalize:
            img /= self._sensor_max_value

        return img


class Proximity(Lidar):
    """
    Proximity Sensors are opposite of Lidar sensor. Close objects have high value.
    """

    sensor_type = SensorTypes.Proximity

    def _compute_raw_sensor(self, playground, *_):

        super()._compute_raw_sensor(playground)

        self.sensor_values = self._sensor_max_value - self.sensor_values


class Touch(Lidar):
    """
    Touch Sensors detect close proximity of Entities to the anchor of the sensor.
    It emulates artificial skin, at the condition that the shape of the anchor is round.

    The range parameter is used to describe the thickness of the artificial skin.
    """

    sensor_type = SensorTypes.TOUCH

    def __init__(self,
                 anchor,
                 invisible_elements=None,
                 normalize=True,
                 noise_params=None,
                 **kwargs):

        super().__init__(anchor=anchor,
                         invisible_elements=invisible_elements,
                         normalize=normalize,
                         noise_params=noise_params,
                         **kwargs)

        self._sensor_max_value = self._max_range
        self._max_range = self._anchor.radius + self._max_range  # pylint: disable=access-member-before-definition

    def _compute_raw_sensor(self, playground, *_):

        super()._compute_raw_sensor(playground)

        distance_to_anchor = self.sensor_values - self._anchor.radius
        distance_to_anchor[distance_to_anchor < 0] = 0
        self.sensor_values = self._sensor_max_value - distance_to_anchor


class PoseSensor(SensorDevice):
    def __init__(self,
                 anchor,
                 noise_params=None,
                 normalize=False,
                 **kwargs):
        super().__init__(anchor=anchor,
                         noise_params=noise_params,
                         fov=1,
                         resolution=1,
                         max_range=1,
                         normalize=normalize,
                         **kwargs)

        self._pg_size = None

    def _get_null_sensor(self):
        return np.zeros(3)

    def set_scale(self, size):
        self._pg_size = np.array(size)

    def _apply_noise(self):
        if self._noise_type == 'gaussian':
            additive_noise = np.random.normal(self._noise_mean,
                                              self._noise_scale,
                                              size=self.shape)

        else:
            raise ValueError

        self.sensor_values += additive_noise

    def draw(self, width: int, height: int):
        img = Image.new("RGB", (width, height), (255, 255, 255))
        drawer_image = ImageDraw.Draw(img)

        fnt = ImageFont.truetype("Pillow/Tests/fonts/FreeMono.ttf", int(height * 1 / 2))
        values_str = ", ".join(["%.2f" % e for e in self.sensor_values])
        w_text, h_text = fnt.getsize(text=values_str)
        pos_text = ((width - w_text) / 2, (height - h_text) / 2)
        drawer_image.text(pos_text,
                          values_str,
                          font=fnt,
                          fill=(0, 0, 0))

        return np.asarray(img) / 255


class Position(PoseSensor):
    def _compute_raw_sensor(self, playground, *_):
        self.sensor_values = np.concatenate([np.array(self._anchor.position),
                                             [self._anchor.angle]])

    def _apply_normalization(self):
        if self._pg_size is not None:
            self.sensor_values[0:2] = self.sensor_values[0:2] / self._pg_size


class Velocity(PoseSensor):
    def _compute_raw_sensor(self, playground, *_):
        self.sensor_values = np.concatenate([np.array(self._anchor.velocity),
                                             [self._anchor.angular_velocity]])

    def _apply_normalization(self):
        pass
