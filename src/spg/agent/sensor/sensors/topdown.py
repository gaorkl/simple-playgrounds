"""
Module that defines TopDown Sensors.
Topdown sensors are based computed using the image provided by the environment.
"""
from __future__ import annotations
from typing import Tuple, TYPE_CHECKING, Optional

import math

import numpy as np
import pygame
from skimage import draw
from skimage.transform import resize, rotate

from spg.agent.sensor.sensor import ImageBasedSensor
from spg.common.definitions import SensorTypes
from spg.configs.parser import parse_configuration


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
                                             SensorTypes.TOPDOWN_LOCAL)
        kwargs = {**default_config, **kwargs}

        super().__init__(anchor=anchor, **kwargs)

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

        if self.only_front:
            self._sensor_size = int(self._resolution / 2), self._resolution, 3
        else:
            self._sensor_size = self._resolution, self._resolution, 3

    def _compute_raw_sensor(self):

        cropped_img = self.playground.view(surface=self._surface,
                                           center=self._anchor.position,
                                           size=self._size_surface,
                                           draw_invisible=False,
                                           invisible_elements=self._invisible_elements)

        img = np.rot90(cropped_img, -1, (1, 0))
        img = img[::-1, :, ::-1]

        small_img = resize(img, (self._resolution, self._resolution),
                           order=0,
                           preserve_range=True,
                           anti_aliasing=self._anti_aliasing)

        rotated_img = rotate(small_img,
                             self._anchor._pm_body.angle * 180 / math.pi + 90)

        masked_img = rotated_img
        masked_img[self.mask_total_fov == 0] = 0

        if self.only_front:
            masked_img = masked_img[:int(self._resolution / 2), ...]

        self.sensor_values = masked_img

    @property
    def shape(self):
        return self._sensor_size[0], self._sensor_size[1], 3


class TopDownGlobal(ImageBasedSensor):
    """
    TopDownGlobal provides an image from bird's eye view of the full playground.
    The anchor only serves for Device Modifiers.

    """
    def __init__(self,
                 anchor,
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

        default_config = parse_configuration('agent_sensors',
                                             SensorTypes.TOPDOWN_GLOBAL)
        kwargs = {**default_config, **kwargs}

        super().__init__(anchor=anchor, **kwargs)

        # Assert that size is set or coming from playground.

        self._size = None
        self._center = None

        self._sensor_max_value = 255.

    @property
    def playground(self):
        return self._playground

    @playground.setter
    def playground(self, playground):

        if playground:
            self._size = playground.size
            self._center = (self._size[0] / 2, self._size[1] / 2)

            self._size_surface = self._size
            # Assert that center is set or coming from playground

            max_size = max(self._size)

            self._sensor_size = (int(self._resolution * self._size[1] / max_size),
                                 int(self._resolution * self._size[0] / max_size))

            self._surface = pygame.Surface(self._size)

        self._playground = playground

    def _get_sensor_image(self):

        global_img = self.playground.view(surface=self._surface,
                                           center=self._center,
                                           size=self._size_surface,
                                           draw_invisible=False,
                                           invisible_elements=self._invisible_elements)


        small_img = resize(global_img, self._sensor_size,
                           order=0,
                           preserve_range=True,
                           anti_aliasing=self._anti_aliasing)

        img = np.rot90(small_img, -1, (1, 0))
        img = img[::-1, :, ::-1]

        return img

    def _compute_raw_sensor(self):

        full_image = self._get_sensor_image()

        self.sensor_values = resize(full_image,
                                    self._sensor_size,
                                    order=0,
                                    preserve_range=True)

    @property
    def shape(self):
        return self._sensor_size[0], self._sensor_size[1], 3

#
# class TopDownGlobal(ImageBasedSensor):
#     """
#     TopDownGlobal provides an image from bird's eye view of the full playground.
#     The anchor only serves for Device Modifiers.
#
#     """
#     def __init__(self,
#                  anchor,
#                  center: Optional[Tuple[int, int]] = None,
#                  size: Optional[Tuple[int, int]] = None,
#                  **kwargs):
#         """
#         Refer to Sensor Class.
#
#         Args:
#             invisible_elements: elements that the sensor does not perceive.
#                 List of Parts of SceneElements.
#             normalize: if true, Sensor values are normalized between 0 and 1.
#                 Default: True
#             only_front: Only return the half part of the Playground that the Sensor faces.
#                 Remove what is behind the sensor. Default: False.
#         """
#
#         default_config = parse_configuration('agent_sensors',
#                                              SensorTypes.TOPDOWN_GLOBAL)
#         kwargs = {**default_config, **kwargs}
#
#         super().__init__(anchor=anchor, **kwargs)
#
#         # Assert that size is set or coming from playground.
#
#         self._size = None
#         if size:
#             self._size = size
#
#         self._center = None
#         if center:
#             self._center = center
#
#         if (center and not size) or (size and not center):
#             raise ValueError('size and center must both be set')
#
#         self._sensor_max_value = 255.
#
#     @property
#     def playground(self):
#         return self._playground
#
#     @playground.setter
#     def playground(self, playground):
#
#         if not self._size:
#             self._size = playground.size
#             self._center = (self._size [0] / 2, self._size [1] / 2)
#         else:
#             raise ValueError("Size must be set either in the Playground or in the sensor")
#
#         self._size_surface = self._size
#         # Assert that center is set or coming from playground
#
#         max_size = max(self._size)
#         self._destination_size = (int(self._resolution * self._size[1] / max_size),
#                                   int(self._resolution * self._size[0] / max_size))
#
#         self._surface = pygame.Surface(self._size)
#
#         self._playground = playground
#
#     def _get_sensor_image(self):
#
#         global_img = self.playground.view(surface=self._surface,
#                                            center=self._center,
#                                            size=self._size_surface,
#                                            draw_invisible=False,
#                                            invisible_elements=self._invisible_elements)
#
#         np_image = np.rot90(global_img, -1, (1, 0))
#         np_image = np_image[::-1, :, ::-1]
#         return np_image
#
#     def _compute_raw_sensor(self):
#
#         full_image = self._get_sensor_image()
#
#         self.sensor_values = resize(full_image,
#                                     self._destination_size,
#                                     order=0,
#                                     preserve_range=True)
#
#     @property
#     def shape(self):
#         return self._destination_size[0], self._destination_size[1], 3
