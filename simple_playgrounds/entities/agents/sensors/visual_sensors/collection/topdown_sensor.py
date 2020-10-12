"""
Module for Top-down Sensor.
"""
import math
import numpy as np

import cv2

from simple_playgrounds.entities.agents.sensors.visual_sensors.visual_sensor import VisualSensor

#pylint: disable=line-too-long
#pylint: disable=too-many-locals
#pylint: disable=no-member


class TopdownSensor(VisualSensor):
    """
    TopdownSensor provides an image from bird's eye view, centered and oriented on the anchor.
    """
    sensor_type = 'topdown'

    def __init__(self, anchor, invisible_elements=None, normalize=True, only_front=False, **kwargs):
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

        super(TopdownSensor, self).__init__(anchor, invisible_elements, normalize, **kwargs)

        self.only_front = only_front

        self._center = ( int(self._resolution/2)-1, int(self._resolution/2)-1)

        mask_total_fov = np.zeros((self._resolution, self._resolution, 3))

        self.mask_total_fov = cv2.ellipse(mask_total_fov, self._center, axes=self._center, angle=0,
                                     startAngle=(-math.pi/2 - self._fov / 2) * 180 / math.pi,
                                     endAngle=(-math.pi/2  + self._fov / 2) * 180 / math.pi,
                                     color=(1, 1, 1), thickness=-1)

    def compute_raw_sensor(self, img):

        small_img = cv2.resize(img, (self._resolution, self._resolution), interpolation=cv2.INTER_NEAREST)

        rot_mat = cv2.getRotationMatrix2D(self._center, self.anchor.pm_body.angle * 180 / math.pi + 90, 1.0)
        rotated_img = cv2.warpAffine(small_img, rot_mat, small_img.shape[1::-1], flags=cv2.INTER_NEAREST)

        masked_img = self.mask_total_fov * rotated_img

        if self.only_front:
            masked_img = masked_img[:int(self._resolution/2), ...]

        self.sensor_value = masked_img[:, ::-1, ::-1]

    @property
    def shape(self):

        if self.only_front:
            return int(self._resolution/2), self._resolution, 3
        return  self._resolution, self._resolution, 3

    def draw(self, width_display, height_sensor):

        h = int(width_display * self.shape[0] / self.shape[1])
        im = cv2.resize(self.sensor_value, (width_display, h), interpolation=cv2.INTER_NEAREST)
        if self.apply_normalization is False: im /= 255.

        return im
