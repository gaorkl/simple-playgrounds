"""
Module for Vision Sensors.
"""
import numpy as np
import cv2
from simple_playgrounds.entities.agents.sensors.visual_sensors.visual_sensor import VisualSensor

#pylint: disable=line-too-long
#pylint: disable=too-many-locals
#pylint: disable=no-member


class RgbSensor(VisualSensor):

    """
    Provides a 1D image from the point of view of the anchor.
    Similar to RGB camera, as a single line of pixels.
    """
    sensor_type = 'rgb'

    def __init__(self, anchor, invisible_elements=None, normalize=True, **kwargs):

        super().__init__(anchor, invisible_elements, normalize=normalize, **kwargs)

    def update_sensor(self, img):

        super().update_sensor(img)

        # Get value sensor
        mask = self.polar_view != 0
        sensor_id = np.min(np.where(mask.any(axis=1), mask.argmax(axis=1),
                                    self.polar_view.shape[1] - 1), axis=1)
        sensor_value = self.polar_view[np.arange(int(self.polar_view.shape[0])), sensor_id, :]

        image = np.asarray(sensor_value)
        image = np.expand_dims(image, 0)
        self.sensor_value = cv2.resize(image, (self._resolution, 1),
                                       interpolation=cv2.INTER_NEAREST)[0, :]

        self.apply_normalization()

    def apply_normalization(self):

        if self.normalize:
            self.sensor_value = self.sensor_value/255.

    @property
    def shape(self):
        return self._resolution, 3

    def draw(self, width_display, height_sensor):

        im = np.expand_dims(self.sensor_value, 0)
        im = cv2.resize(im, (width_display, height_sensor), interpolation=cv2.INTER_NEAREST)
        if self.apply_normalization is False: im /= 255.

        return im

class GreySensor(VisualSensor):
    """
    Provides a 1D image from the point of view of the anchor.
    Similar to Grey-level camera, as a single line of pixels.
    """
    sensor_type = 'grey'

    def __init__(self, anchor, invisible_elements=None, normalize=True, **kwargs):
        super().__init__(anchor, invisible_elements, normalize=normalize, **kwargs)

    def update_sensor(self, img):
        super().update_sensor(img)

        # Get value sensor
        mask = self.polar_view != 0
        sensor_id = np.min(np.where(mask.any(axis=1), mask.argmax(axis=1),
                                    self.polar_view.shape[1] - 1), axis=1)
        sensor_value = self.polar_view[np.arange(int(self.polar_view.shape[0])), sensor_id, :]

        image = np.asarray(sensor_value)
        image = np.expand_dims(image, 0)

        image = cv2.resize(image, (self._resolution, 1),
                           interpolation=cv2.INTER_NEAREST)[0, :]

        image = np.expand_dims(image, 0)
        image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        image = cv2.resize(image, (self._resolution, 1),
                           interpolation=cv2.INTER_NEAREST)[0, :]

        self.sensor_value = image

        self.apply_normalization()

    @property
    def shape(self):
        return self._resolution

    def draw(self, width_display, height_sensor):

        expanded = np.zeros((self.shape, 3))
        for i in range(3):
            expanded[:, i] = self.sensor_value[:]
        im = np.expand_dims(expanded, 0)
        im = cv2.resize(im, (width_display, height_sensor), interpolation=cv2.INTER_NEAREST)

        if self.normalize is False: im /= 255.

        return im

    def apply_normalization(self):

        if self.normalize:
            self.sensor_value = self.sensor_value/255.