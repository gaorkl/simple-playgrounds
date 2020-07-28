"""
Module defining Depth Sensor
"""
import numpy as np
import cv2

from simple_playgrounds.entities.agents.sensors.visual_sensors.visual_sensor import VisualSensor

# pylint: disable=no-member


class DepthSensor(VisualSensor):

    """Depth Sensor calculates a Depth image from the point of view of the agent.
    Similar to a Depth Camera.
    """

    sensor_type = 'depth'

    def __init__(self, anchor, invisible_elements=None, normalize=True, **kwargs):

        super(DepthSensor, self).__init__(anchor, invisible_elements, normalize, **kwargs)

        self._value_range = self._range

    def update_sensor(self, img):

        super().update_sensor(img)

        mask = self.polar_view != 0
        sensor = np.min(np.where(mask.any(axis=1), mask.argmax(axis=1),
                                 self.polar_view.shape[1] ), axis=1)

        sensor_value = self._range*(self.polar_view.shape[1] - sensor)/self.polar_view.shape[1]

        image = np.asarray(sensor_value)
        image = np.expand_dims(image, 0)
        self.sensor_value = cv2.resize(image, (self._resolution, 1),
                                       interpolation=cv2.INTER_NEAREST)[0, :]

        self.apply_normalization()

    def apply_normalization(self):

        if self.normalize:
            self.sensor_value = self.sensor_value * 1.0 / self._range

    @property
    def shape(self):
        return self._resolution

    def draw(self, width_display, height_sensor):

        expanded = np.zeros((self.shape, 3))
        for i in range(3):
            expanded[:, i] = self.sensor_value[:]
        img = np.expand_dims(expanded, 0)
        img = cv2.resize(img, (width_display, height_sensor), interpolation=cv2.INTER_NEAREST)

        if self.apply_normalization is False:
            img *= 1.0 / self._range

        return img
