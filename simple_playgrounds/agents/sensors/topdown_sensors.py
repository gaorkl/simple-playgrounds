"""
Module that defines TopDown Sensors.
Topdown sensors are based computed using the image provided by the environment.
"""
import numpy as np
import math
import cv2
import pygame

from .sensor import Sensor
from ...utils.definitions import SensorModality


class TopdownSensor(Sensor):
    """
    TopdownSensor provides an image from bird's eye view, centered and oriented on the anchor.
    """
    sensor_type = 'topdown'
    sensor_modality = SensorModality.VISUAL

    def __init__(self, anchor, invisible_elements=None, normalize=True, noise_params=None, only_front=False, **sensor_params):
        """
        Refer to VisualSensor Class.

        Args:
            anchor: body Part to which the sensor is attached.
                Sensor is attached to the center of the Part.
            invisible_elements: elements that the sensor does not perceive. List of Parts of SceneElements.
            normalize: if true, Sensor values are normalized between 0 and 1.
                Default: True
            only_front: Only return the half part of the Playground that the Sensor faces.
                Remove what is behind the sensor. Default: False.
        """

        default_config = self._parse_configuration()
        sensor_params = {**default_config, **sensor_params}

        super().__init__(anchor=anchor, invisible_elements=invisible_elements, normalize=normalize,
                         noise_params=noise_params, **sensor_params)

        assert self._resolution > 0
        assert self._fov > 0
        assert self._range > 0

        self.only_front = only_front

        self._center = (int(self._resolution / 2) - 1, int(self._resolution / 2) - 1)

        mask_total_fov = np.zeros((self._resolution, self._resolution, 3))

        self.mask_total_fov = cv2.ellipse(mask_total_fov, self._center, axes=self._center, angle=0,
                                          startAngle=(-math.pi / 2 - self._fov / 2) * 180 / math.pi,
                                          endAngle=(-math.pi / 2 + self._fov / 2) * 180 / math.pi,
                                          color=(1, 1, 1), thickness=-1)

    def get_local_sensor_image(self, pg, sensor_surface):

        all_agent_parts = []
        for agent in pg.agents:
            all_agent_parts += agent.parts

        # take all elems and body parts which are close to sensor
        sc_elems = [elem for elem in pg.scene_elements if
                    self._check_elem(elem)]
        sc_elems += [elem for elem in all_agent_parts if
                     self._check_elem(elem)]

        # filter invisible
        visible_sc_elems = [elem for elem in sc_elems if elem not in self._invisible_elements]

        # Draw elements that are not invisible to this agent
        for element in visible_sc_elems:
            element.draw(sensor_surface)

        cropped = pygame.Surface((2 * self._range + 1, 2 * self._range + 1))

        pos_x = self.anchor.position[0] + self._range - pg.width
        pos_y = - self.anchor.position[1] + self._range
        cropped.blit(sensor_surface, (pos_x, pos_y))

        img_cropped = pygame.surfarray.pixels3d(cropped).astype(float)

        return img_cropped

    def _check_elem(self, elem):

        if elem.pm_visible_shape is not None:
            contact_points = elem.pm_visible_shape.shapes_collide(self.anchor.pm_visible_shape).points
            return (not elem.background) and len(contact_points) == 0

        return not elem.background

    def _compute_raw_sensor(self, playground, sensor_surface, **kwargs):

        cropped_img = self.get_local_sensor_image(playground, sensor_surface)

        small_img = cv2.resize(cropped_img, (self._resolution, self._resolution), interpolation=cv2.INTER_NEAREST)

        rot_mat = cv2.getRotationMatrix2D(self._center, self.anchor.pm_body.angle * 180 / math.pi + 90, 1.0)
        rotated_img = cv2.warpAffine(small_img, rot_mat, small_img.shape[1::-1], flags=cv2.INTER_NEAREST)

        masked_img = self.mask_total_fov * rotated_img

        if self.only_front:
            masked_img = masked_img[:int(self._resolution / 2), ...]

        self.sensor_value = masked_img[:, ::-1, ::-1]

    def _apply_normalization(self):
        self.sensor_value /= 255.

    @property
    def shape(self):

        if self.only_front:
            return int(self._resolution / 2), self._resolution, 3
        return self._resolution, self._resolution, 3

    def draw(self, width_display, height_display=None, **kwargs):

        if height_display is None:
            height_display = int(width_display * self.shape[0] / self.shape[1])

        im = cv2.resize(self.sensor_value, (width_display, height_display),
                        interpolation=cv2.INTER_NEAREST)
        if not self._apply_normalization:
            im /= 255.

        return im
