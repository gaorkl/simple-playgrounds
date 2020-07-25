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

    def update_sensor(self, img):

        width, height, _ = img.shape

        # Position of the sensor
        sensor_x, sensor_y = self.anchor.pm_body.position
        sensor_x, sensor_y = int(sensor_x), int(sensor_y)
        sensor_angle = (math.pi / 2 - self.anchor.pm_body.angle)

        mask_total_fov = np.zeros((width, height, 3))
        center = height - int(sensor_y), width - int(sensor_x)
        # cv2.circle(mask_total_fov, center, self.fovRange, (255, 255, 255), thickness=-1)

        mask_total_fov = cv2.ellipse(mask_total_fov, center, axes=(self._range, self._range), angle=0,
                                     startAngle=(math.pi + sensor_angle - self._fov / 2) * 180 / math.pi,
                                     endAngle=(math.pi + sensor_angle + self._fov / 2) * 180 / math.pi,
                                     color=(1, 1, 1), thickness=-1)

        masked_img = mask_total_fov * img

        x_start_crop = int(max(0, center[1] - self._range))
        x_end_crop = int(min(width, center[1] + self._range))

        y_start_crop = int(max(0, center[0] - self._range))
        y_end_crop = int(min(height, center[0] + self._range))

        extended_cropped = np.zeros(((2*self._range + 1), (2 * self._range + 1), 3))

        extended_cropped[self._range - (center[1] - x_start_crop):self._range + (x_end_crop - center[1]),
                         self._range - (center[0] - y_start_crop):self._range + (y_end_crop - center[0]), :]\
                         = masked_img[x_start_crop:x_end_crop, y_start_crop:y_end_crop, :]

        image_center = tuple(np.array(extended_cropped.shape[1::-1]) / 2)
        rot_mat = cv2.getRotationMatrix2D(image_center, sensor_angle*180/math.pi - 90, 1.0)
        result = cv2.warpAffine(extended_cropped, rot_mat, extended_cropped.shape[1::-1], flags=cv2.INTER_NEAREST)

        if self.only_front:
            result = result[:self._range, :, :]
            self.sensor_value = cv2.resize(result, (2*self._resolution, self._resolution),
                                           interpolation=cv2.INTER_NEAREST)
        else:
            self.sensor_value = cv2.resize(result, (2*self._resolution, 2*self._resolution),
                                           interpolation=cv2.INTER_NEAREST)

        self.apply_normalization()

    def apply_normalization(self):

        if self.normalize:
            self.sensor_value = self.sensor_value/255.

    @property
    def shape(self):

        if self.only_front:
            return self._resolution, 2 * self._resolution, 3
        return 2 * self._resolution, 2 * self._resolution, 3

    def draw(self, width_display, height_sensor):

        h = int(width_display * self.shape[0] / self.shape[1])
        im = cv2.resize(self.sensor_value, (width_display, h), interpolation=cv2.INTER_NEAREST)
        if self.apply_normalization is False: im /= 255.

        return im