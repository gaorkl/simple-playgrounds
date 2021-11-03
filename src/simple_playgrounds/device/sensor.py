"""
Module defining the Base Classes for Sensors.
"""

from __future__ import annotations
from typing import List, Dict, Optional, Union, Tuple, TYPE_CHECKING
if TYPE_CHECKING:
    from simple_playgrounds.playground.playground import Playground

import math
from abc import abstractmethod, ABC
from operator import attrgetter

import numpy as np
import pymunk
from pygame import Surface
from PIL import Image, ImageDraw, ImageFont
from skimage.transform import resize

from simple_playgrounds.device.device import Device
from simple_playgrounds.agent.parts import Part
from simple_playgrounds.common.entity import Entity
from simple_playgrounds.element.element import SceneElement


class SensorDevice(Device):
    """ Base class Sensor, used as an Interface for all sensors.

    Attributes:
        anchor: Part or Element to which the sensor is attached.
            Sensor is attached to the center of the anchor.
        sensor_values: current values of the sensor.
        name: Name of the sensor.

    Note:
        The anchor is always invisible to the sensor.

    """

    _index_sensor = 0

    def __init__(self,
                 anchor: Union[Part, SceneElement],
                 noise_params: Optional[Dict] = None,
                 normalize: Optional[bool] = False,
                 name: Optional[str] = None,
                 **kwargs,
                 ):
        """
        Sensors are attached to an anchor.
        They can detect any visible Part of an Agent or Elements of the Playground.
        If the entity is in invisible elements, it is not detected.

        Args:
            anchor: Body Part or Scene Element on which the sensor will be attached.
            normalize: boolean. If True, sensor values are scaled between 0 and 1.
            noise_params: Dictionary of noise parameters.
                Noise is applied to the raw sensor, before normalization.
            name: name of the sensor. If not provided, a name will be set by default.

        Noise Parameters:
            type: 'gaussian', 'salt_pepper'
            mean: mean of gaussian noise (default 0)
            scale: scale (or std) of gaussian noise (default 1)
            salt_pepper_probability: probability for a pixel to be turned off or max

        """

        Device.__init__(self, anchor=anchor)

        # Sensor name
        # Internal counter to assign number and name to each sensor
        if name:
            self.name = name
        else:
            self.name = self.__class__.__name__.lower() + '_' + str(
                SensorDevice._index_sensor)
            SensorDevice._index_sensor += 1

        self.sensor_values = None

        self._normalize = normalize

        self._noise = False
        if noise_params is not None:
            self._noise = True
            self._noise_type = noise_params.get('type', 'gaussian')

            if self._noise_type == 'gaussian':
                self._noise_mean = noise_params.get('mean', 0)
                self._noise_scale = noise_params.get('scale', 1)

            elif self._noise_type == 'salt_pepper':
                self._noise_probability = noise_params.get('probability', 0.1)

            else:
                raise ValueError('Noise type not implemented')

        # Sensor max value is used for noise and normalization calculation
        self._sensor_max_value: float = 0.

        # If it requires a topdown representation of the playground
        # to compute the sensor values
        self.requires_surface: bool = False
        self.requires_playground_size: bool = False
        self._pg_size: Optional[Tuple[int, int]] = None

    def update(self, playground: Playground, sensor_surface: Surface):

        if self._disabled:
            self.sensor_values = self._get_null_sensor()

        else:
            self._compute_raw_sensor(playground, sensor_surface)

            if self._noise:
                self._apply_noise()

            if self._normalize:
                self._apply_normalization()

    @abstractmethod
    def _compute_raw_sensor(
        self,
        playground: Playground,
        sensor_surface: Surface,
    ):
        ...

    @abstractmethod
    def _apply_normalization(self):
        ...

    @abstractmethod
    def _apply_noise(self):
        ...

    @abstractmethod
    def _get_null_sensor(self):
        ...

    @property
    @abstractmethod
    def shape(self):
        """ Returns the shape of the numpy array, if applicable."""
        ...

    @abstractmethod
    def draw(self, width: int, height: int):
        """
        Function that creates an image for visualizing a sensor.

        Keyword Args:
            width: width of the returned image
            height: when applicable (in the case of 1D sensors), the height of the image.

        Returns:
            Numpy array containing the visualization of the sensor values.

        """
        ...

    def set_playground_size(self, size):
        pass


##################
# External Sensors
##################

class ExternalSensor(SensorDevice, ABC):

    def __init__(self,
                 anchor,
                 fov: float,
                 resolution: int,
                 max_range: float,
                 min_range: float,
                 invisible_elements: Optional[Union[List[Entity],
                                                    Entity]] = None,
                 **kwargs,
                 ):

        """

        Args:
            fov: Field of view of the sensor (in degrees).
            resolution: Resolution of the sensor (depends on the sensor).
            max_range: maximum range of the sensor (in units of distance).
            min_range: minimum range of the sensor (in units of distance).
            invisible_elements: Optional list of elements invisible to the sensor.
            **kwargs:

        """

        super().__init__(anchor, **kwargs)

        self._invisible_elements: List[Entity]

        # Invisible elements
        if not invisible_elements:
            self._invisible_elements = []
        elif isinstance(invisible_elements, Entity):
            self._invisible_elements = [invisible_elements]
        else:
            self._invisible_elements = invisible_elements

        self._min_range = min_range
        self._max_range = max_range
        self._fov = fov * math.pi / 180
        self._resolution = resolution

        if self._resolution < 0:
            raise ValueError('resolution must be more than 1')
        if self._fov < 0:
            raise ValueError('field of view must be more than 1')
        if self._max_range < 0:
            raise ValueError('maximum range must be more than 1')
        if self._min_range < 0:
            raise ValueError('minimum range must be more than 1')

        # Temporary invisible to manage elements that are invisible to the agent or sensor.
        # Manages dynamic invisibility. Elements are invisible some times.
        self._temporary_invisible: List[Entity] = []

    def pre_step(self):
        super().pre_step()
        self._temporary_invisible = []

    def set_temporary_invisible(self, temporary_invisible: List[Entity]):
        self._temporary_invisible = temporary_invisible


class RayBasedSensor(ExternalSensor, ABC):
    """
    Base class for Ray Based sensors.
    Ray collisions are computed using pymunk segment queries.
    They detect intersection with obstacles.
    Robotic sensors and Semantic sensors inherit from this class.

    """
    def __init__(
        self,
        anchor,
        remove_duplicates: Optional[bool] = False,
        **kwargs,
    ):
        """
        Args:
            remove_duplicates: If True, removes detections of the same objects on multiple rays.
                Keeps the closest detection.
            **kwargs: Additional sensor params.

        Notes:
         Three approaches can be used to prevent a sensor from detecting the parts of an agent.

         (1) Do not set min_range and invisible_elements.
         In this case the min_range will by default be set to the correct value to start detection after
         the anchor.
         The computation of robotic and semantic sensors is in general faster with this approach.
         However this approach might be limited to the case of simple agents with only a base.

         (2) Set min_range large enough so that the sensors start at a reasonable distance.

         (3) Use the invisible_elements argument to make all parts
         of the agent invisible.
         This approach is slightly slower but easier to implement and use.

        """

        super().__init__(anchor, **kwargs)

        self._remove_duplicates = remove_duplicates

        # Rays need to start at least after anchor
        if (self._anchor not in self._invisible_elements) \
                and (self._min_range < self._anchor.radius + 1):
            self._min_range = self._anchor.radius + 1

        # Field of View of the Sensor
        if self._resolution == 1:
            self._ray_angles = [0.]
        else:
            self._ray_angles = [
                n * self._fov / (self._resolution - 1) - self._fov / 2
                for n in range(self._resolution)
            ]

    @staticmethod
    def _remove_duplicate_collisions(
            collisions_by_angle: Dict[float,
                                      Optional[pymunk.SegmentQueryInfo]]):

        all_shapes = list(
            set(col.shape for angle, col in collisions_by_angle.items()
                if col))

        all_collisions = []
        for angle, col in collisions_by_angle.items():
            if col:
                all_collisions.append(col)

        all_min_collisions = []
        for shape in all_shapes:
            min_col = min(
                [col for col in all_collisions if col.shape is shape],
                key=attrgetter('alpha'))
            all_min_collisions.append(min_col)

        # Filter out noon-min collisions
        for angle, col in collisions_by_angle.items():
            if col and col not in all_min_collisions:
                collisions_by_angle[angle] = None

        return collisions_by_angle

    def _compute_collision(
        self,
        playground: Playground,
        sensor_angle: float,
    ) -> Optional[pymunk.SegmentQueryInfo]:

        position_body = self._anchor.pm_body.position
        angle = self._anchor.pm_body.angle + sensor_angle

        position_end = position_body + pymunk.Vec2d(self._max_range,
                                                    0).rotated(angle)

        position_start = position_body + pymunk.Vec2d(self._min_range + 1,
                                                      0).rotated(angle)

        inv_shapes = []
        for elem in self._invisible_elements + self._temporary_invisible:
            if elem.pm_visible_shape and not elem.pm_visible_shape.sensor:
                elem.pm_visible_shape.sensor = True
                inv_shapes.append(elem.pm_visible_shape)

        collision = playground.space.segment_query_first(
            position_start, position_end, 1, shape_filter=pymunk.ShapeFilter(pymunk.ShapeFilter.ALL_MASKS()))

        for shape in inv_shapes:
            shape.sensor = False

        return collision

    def _compute_points(
        self,
        playground: Playground,
    ) -> Dict[float, Optional[pymunk.SegmentQueryInfo]]:

        points = {}

        for sensor_angle in self._ray_angles:
            collision = self._compute_collision(playground, sensor_angle)
            points[sensor_angle] = collision

        if self._remove_duplicates:
            points = self._remove_duplicate_collisions(points)

        return points

    def _apply_noise(self):

        if self._noise_type == 'gaussian':
            additive_noise = np.random.normal(self._noise_mean,
                                              self._noise_scale,
                                              size=self.shape)

        elif self._noise_type == 'salt_pepper':
            prob = [
                self._noise_probability / 2, 1 - self._noise_probability,
                self._noise_probability / 2
            ]
            additive_noise = np.random.choice(
                [-self._sensor_max_value, 0, self._sensor_max_value],
                p=prob,
                size=self.shape)

        else:
            raise ValueError

        self.sensor_values += additive_noise

        self.sensor_values[self.sensor_values < 0] = 0
        self.sensor_values[self.sensor_values >
                           self._sensor_max_value] = self._sensor_max_value


class ImageBasedSensor(ExternalSensor, ABC):

    """
    Base class for Image Based sensors.
    Image based sensors are computed using the top-down rendering of the playground.

    """

    def __init__(
            self,
            anchor,
            **kwargs,
    ):
        super().__init__(anchor, **kwargs)

    def _apply_normalization(self):
        self.sensor_values /= self._sensor_max_value

    def _apply_noise(self):

        if self._noise_type == 'gaussian':

            additive_noise = np.random.normal(self._noise_mean,
                                              self._noise_scale,
                                              size=self.shape)

        elif self._noise_type == 'salt_pepper':

            proba = [
                self._noise_probability / 2, 1 - self._noise_probability,
                self._noise_probability / 2
            ]
            additive_noise = np.random.choice(
                [-self._sensor_max_value, 0, self._sensor_max_value],
                p=proba,
                size=self.shape)

        else:
            raise ValueError

        self.sensor_values += additive_noise

        self.sensor_values[self.sensor_values < 0] = 0
        self.sensor_values[self.sensor_values >
                           self._sensor_max_value] = self._sensor_max_value

    def _get_null_sensor(self):
        return np.zeros(self.shape)

    def draw(self, width, *_):

        height_display = int(width * self.shape[0] / self.shape[1])

        image = resize(self.sensor_values, (height_display, width),
                       order=0,
                       preserve_range=True)

        if not self._normalize:
            image /= 255.

        return image

##################
# Internal Sensors
##################


class InternalSensor(SensorDevice, ABC):

    """
    Base Class for Internal Sensors.
    """

    def _get_null_sensor(self):
        return np.zeros(self.shape)

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

        if self.sensor_values is not None:
            fnt = ImageFont.truetype("Pillow/Tests/fonts/FreeMono.ttf", int(height * 1 / 2))
            values_str = ", ".join(["%.2f" % e for e in self.sensor_values])
            w_text, h_text = fnt.getsize(text=values_str)
            pos_text = ((width - w_text) / 2, (height - h_text) / 2)
            drawer_image.text(pos_text,
                              values_str,
                              font=fnt,
                              fill=(0, 0, 0))

        return np.asarray(img) / 255.
