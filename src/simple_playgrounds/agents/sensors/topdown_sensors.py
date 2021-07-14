"""
Module that defines TopDown Sensors.
Topdown sensors are based computed using the image provided by the environment.
"""
from typing import Tuple, List, Union

import math
import numpy as np

from skimage.transform import resize, rotate
from skimage import draw
import pygame


from .sensor import Sensor
from ...common.definitions import SensorTypes
from ...configs.parser import parse_configuration
from ...playgrounds.playground import Playground
# pylint: disable=no-member


class TopdownSensor(Sensor):
    """
    TopdownSensor provides an image from bird's eye view, centered and oriented on the anchor.
    The anchor is, by default, visible to the agent.
    """

    def __init__(self,
                 anchor,
                 invisible_elements=None,
                 normalize=True,
                 noise_params=None,
                 only_front=False,
                 **sensor_params):
        """
        Refer to Sensor Class.

        Args:
            anchor: body Part to which the sensor is attached.
                Sensor is attached to the center of the Part.
            invisible_elements: elements that the sensor does not perceive.
                List of Parts of SceneElements.
            normalize: if true, Sensor values are normalized between 0 and 1.
                Default: True
            only_front: Only return the half part of the Playground that the Sensor faces.
                Remove what is behind the sensor. Default: False.
        """

        default_config = parse_configuration('agent_sensors', SensorTypes.TOP_DOWN)
        sensor_params = {**default_config, **sensor_params}

        super().__init__(anchor=anchor,
                         invisible_elements=invisible_elements,
                         normalize=normalize,
                         noise_params=noise_params,
                         **sensor_params)

        if invisible_elements:
            self._invisible_elements = invisible_elements
        else:
            self._invisible_elements = []

        self.only_front = only_front

        self._center = (int(self._resolution / 2) - 1,
                        int(self._resolution / 2) - 1)

        # Calculate range with circle

        mask_circle = np.zeros((self._resolution, self._resolution),
                               dtype=bool)
        rr, cc = draw.disk((self._center[0], self._center[1]),
                           (int(self._resolution / 2) - 1),
                           shape=mask_circle.shape)
        mask_circle[rr, cc] = 1

        # Calculate fov with poly

        points = [[(int(self._resolution / 2) - 1), 0], [0, 0],
                  [0, self._resolution],
                  [(int(self._resolution / 2) - 1), self._resolution]]

        if self._fov > math.pi:
            points = [[self._resolution, 0]
                      ] + points + [[self._resolution, self._resolution]]

        r1 = self._center[0] - (int(self._resolution / 2) -
                                1) * np.sin(math.pi / 2 + self._fov / 2)
        c1 = self._center[1] + (int(self._resolution / 2) -
                                1) * np.cos(math.pi / 2 + self._fov / 2)

        r2 = self._center[0] - (int(self._resolution / 2) -
                                1) * np.sin(math.pi / 2 - self._fov / 2)
        c2 = self._center[1] + (int(self._resolution / 2) -
                                1) * np.cos(math.pi / 2 - self._fov / 2)

        points = points + [[r2, c2], self._center, [r1, c1]]
        mask_poly = draw.polygon2mask((self._resolution, self._resolution),
                                      np.array(points))

        self.mask_total_fov = mask_circle & mask_poly

        self._sensor_max_value = 255

        self.requires_surface = True

    def apply_shape_filter(self,
                           sensor_collision_index,
                           ) -> bool:
        return False

    def _get_sensor_image(self, playground: Playground, sensor_surface: pygame.Surface):

        for agent in playground.agents:
            for part in agent.parts:
                if part not in self._invisible_elements:
                    part.draw(sensor_surface)

        for elem in playground.elements:
            if not elem.background and elem not in self._invisible_elements:
                elem.draw(sensor_surface)

        cropped = pygame.Surface(
            (2 * self._max_range + 1, 2 * self._max_range + 1))

        # Check that this is correct:
        pos_x = playground.size[1] - (self.anchor.position[0] + self._max_range)
        pos_y = playground.size[1] - (self.anchor.position[1] + self._max_range)
        cropped.blit(sensor_surface, (pos_x, pos_y))

        img_cropped = pygame.surfarray.pixels3d(cropped).astype(float)

        return img_cropped

    def _compute_raw_sensor(self, playground:Playground, sensor_surface: pygame.Surface):

        cropped_img = self._get_sensor_image(playground, sensor_surface)

        small_img = resize(cropped_img, (self._resolution, self._resolution),
                           order=0,
                           preserve_range=True)

        rotated_img = rotate(small_img,
                             -self.anchor.pm_body.angle * 180 / math.pi + 180)

        masked_img = rotated_img
        masked_img[self.mask_total_fov == 0] = 0

        if self.only_front:
            masked_img = masked_img[:int(self._resolution / 2), ...]

        self.sensor_values = masked_img[:, ::-1, ::-1]

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

    @property
    def shape(self):

        if self.only_front:
            return int(self._resolution / 2), self._resolution, 3
        return self._resolution, self._resolution, 3

    def draw(self, width, *_):

        height_display = int(width * self.shape[0] / self.shape[1])

        image = resize(self.sensor_values, (height_display, width),
                       order=0,
                       preserve_range=True)

        if not self._apply_normalization:
            image /= 255.

        return image


class FullPlaygroundSensor(Sensor):
    """
    FullPlaygroundSensor provides an image from bird's eye view of the full playground.
    There is no anchor.
    """

    def __init__(self,
                 anchor,
                 invisible_elements=None,
                 normalize=True,
                 noise_params=None,
                 **kwargs):
        """
        Refer to Sensor Class.

        Args:
            invisible_elements: elements that the sensor does not perceive.
                List of Parts of SceneElements.
            normalize: if true, Sensor values are normalized between 0 and 1.
                Default: True
            only_front: Only return the half part of the Playground that the Sensor faces.
                Remove what is behind the sensor. Default: False.
        """

        default_config = parse_configuration('agent_sensors', SensorTypes.FULL_PLAYGROUND)
        kwargs = {**default_config, **kwargs}

        super().__init__(anchor=anchor,
                         invisible_elements=invisible_elements,
                         normalize=normalize,
                         noise_params=noise_params,
                         **kwargs)

        if invisible_elements:
            self._invisible_elements = invisible_elements
        else:
            self._invisible_elements = []

        self._scale = None

        self._sensor_max_value = 255

        self.requires_surface = True
        self.requires_scale = True

    def apply_shape_filter(self,
                           sensor_collision_index,
                           ) -> bool:

        return False

    def _get_sensor_image(self, playground: Playground, sensor_surface: pygame.Surface):

        for agent in playground.agents:
            for part in agent.parts:
                if part not in self._invisible_elements:
                    part.draw(sensor_surface)

        for elem in playground.elements:
            if not elem.background and elem not in self._invisible_elements:
                elem.draw(sensor_surface)

        img = pygame.surfarray.pixels3d(sensor_surface).astype(float)
        np_image = np.rot90(img, -1, (1, 0))
        np_image = np_image[::-1, :, ::-1]
        return np_image

    def _compute_raw_sensor(self, playground: Playground, sensor_surface: pygame.Surface):

        full_image = self._get_sensor_image(playground, sensor_surface)

        self.sensor_values = resize(full_image,
                                    (self._scale[0], self._scale[1]),
                                    order=0,
                                    preserve_range=True)

    def set_scale(self, size_playground: Union[List[float], Tuple[float, float]]):

        max_size = max(size_playground)
        self._scale = (int(self._resolution * size_playground[1] / max_size),
                       int(self._resolution * size_playground[0] / max_size))

    def _apply_normalization(self):
        self.sensor_values /= self._sensor_max_value

    def _apply_noise(self):

        if self._noise_type == 'gaussian':

            additive_noise = np.random.normal(self._noise_mean,
                                              self._noise_scale,
                                              size=self.shape)

        elif self._noise_type == 'salt_pepper':

            additive_noise = np.random.choice(
                [-self._sensor_max_value, 0, self._sensor_max_value],
                p=[
                    self._noise_probability / 2, 1 - self._noise_probability,
                    self._noise_probability / 2
                ],
                size=self.shape)

        else:
            raise ValueError

        self.sensor_values += additive_noise

        self.sensor_values[self.sensor_values < 0] = 0
        self.sensor_values[self.sensor_values >
                           self._sensor_max_value] = self._sensor_max_value

    @property
    def shape(self):

        return self._scale[0], self._scale[1], 3

    def draw(self, width, *_):

        height_display = int(width * self.shape[0] / self.shape[1])

        image = resize(self.sensor_values, (height_display, width),
                       order=0,
                       preserve_range=True)

        if not self._apply_normalization:
            image /= 255.

        return image
