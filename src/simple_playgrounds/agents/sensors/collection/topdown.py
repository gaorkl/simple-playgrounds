"""
Module that defines TopDown Sensors.
Topdown sensors are based computed using the image provided by the environment.
"""
from __future__ import annotations
from typing import Tuple, List, Union, TYPE_CHECKING
if TYPE_CHECKING:
    from simple_playgrounds.playgrounds.playground import Playground

import math

import numpy as np
import pygame
from skimage import draw
from skimage.transform import resize, rotate

from simple_playgrounds.agents.sensors.sensor import ImageBasedSensor
from simple_playgrounds.common.definitions import SensorTypes
from simple_playgrounds.configs.parser import parse_configuration


# pylint: disable=no-member


class TopdownLocal(ImageBasedSensor):
    """
    TopdownSensor provides an image from bird's eye view, centered and oriented on the anchor.
    The anchor is, by default, visible to the agent.
    """
    def __init__(self, anchor, only_front=False, **kwargs):
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

        default_config = parse_configuration('agent_sensors',
                                             SensorTypes.TOP_DOWN)
        kwargs = {**default_config, **kwargs}

        super().__init__(anchor, **kwargs)

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

    def _get_sensor_image(self, playground: Playground,
                          sensor_surface: pygame.Surface):

        for agent in playground.agents:
            for part in agent.parts:
                if part not in self._invisible_elements:
                    part.draw(sensor_surface)

        for elem in playground.elements:
            if not elem.background and elem not in self._invisible_elements:
                elem.draw(sensor_surface)

        cropped = pygame.Surface(
            (2 * self._max_range + 1, 2 * self._max_range + 1))

        pos_x = -self._anchor.position[0] + self._max_range
        pos_y = -self._anchor.position[1] + self._max_range

        cropped.blit(sensor_surface, (pos_x, pos_y))

        img_cropped = pygame.surfarray.pixels3d(cropped).astype(float)

        return img_cropped

    def _compute_raw_sensor(self, playground: Playground,
                            sensor_surface: pygame.Surface):

        cropped_img = self._get_sensor_image(playground, sensor_surface)

        small_img = resize(cropped_img, (self._resolution, self._resolution),
                           order=0,
                           preserve_range=True)

        rotated_img = rotate(small_img,
                             -self._anchor.pm_body.angle * 180 / math.pi + 180)

        masked_img = rotated_img
        masked_img[self.mask_total_fov == 0] = 0

        if self.only_front:
            masked_img = masked_img[:int(self._resolution / 2), ...]

        self.sensor_values = masked_img[:, ::-1, ::-1]

    @property
    def shape(self):

        if self.only_front:
            return int(self._resolution / 2), self._resolution, 3
        return self._resolution, self._resolution, 3


class TopDownGlobal(ImageBasedSensor):
    """
    FullPlaygroundSensor provides an image from bird's eye view of the full playground.
    There is no anchor.
    """
    def __init__(self, anchor, **kwargs):
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

        default_config = parse_configuration('agent_sensors',
                                             SensorTypes.FULL_PLAYGROUND)
        kwargs = {**default_config, **kwargs}

        super().__init__(anchor, **kwargs)

        self._scale = None

        self._sensor_max_value = 255.

        self.requires_surface = True

    def _get_sensor_image(self, playground: Playground,
                          sensor_surface: pygame.Surface):

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

    def _compute_raw_sensor(self, playground: Playground,
                            sensor_surface: pygame.Surface):

        full_image = self._get_sensor_image(playground, sensor_surface)

        self.sensor_values = resize(full_image,
                                    (self._scale[0], self._scale[1]),
                                    order=0,
                                    preserve_range=True)

    def set_playground_size(self, size: Union[List[float], Tuple[float, float]]):
        super().set_playground_size(size)

        # Compute the scaling for the sensor value
        max_size = max(size)
        self._scale = (int(self._resolution * size[1] / max_size),
                       int(self._resolution * size[0] / max_size))

    @property
    def shape(self):
        return self._scale[0], self._scale[1], 3
