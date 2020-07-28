"""
Module that defines Touch Sensor.
"""
import numpy as np
import cv2

from simple_playgrounds.entities.agents.sensors.visual_sensors.visual_sensor import VisualSensor


class TouchSensor(VisualSensor):
    """
    TopdownSensor provides an array from the point of view of the Anchor.
    It indicates whether other Shapes are in proximity.
    It is similar to a synthetic skin detecting contact points.
    It is intended to be used with Circular anchors.
    """

    # cvbxc

    sensor_type = 'touch'

    def __init__(self, anchor, invisible_elements=None, normalize=True, **kwargs):
        """
        Args:
            anchor: body Part to which the sensor is attached.
                Sensor is attached to the center of the Part.
            invisible_elements: elements that the sensor does not perceive.
                List of Parts of SceneElements.
            normalize: if true, Sensor values are normalized between 0 and 1.
                Default: True.
            **kwargs: Other parameters. Refer to VisualSensor.

        Note:
            Touch sensor is always normalized.
        """

        super(TouchSensor, self).__init__(anchor, invisible_elements, normalize=normalize,
                                          min_range=anchor.radius, **kwargs)

        self._range = self._min_range + self._range

        self._value_range = self._range

    def update_sensor(self, img):

        # pylint: disable=no-member

        super().update_sensor(img)

        # Get value sensor
        if np.sum(self.polar_view) != 0:
            mask = self.polar_view != 0
            sensor = np.min(np.where(mask.any(axis=1), mask.argmax(axis=1),
                                     self.polar_view.shape[1] ), axis=1)

            sensor_value = (self._range - self._min_range) * (self.polar_view.shape[1] - sensor )/self.polar_view.shape[1]
            image = np.asarray(sensor_value)
            image = np.expand_dims(image, 0)

            self.sensor_value = cv2.resize(image, (self._resolution, 1),
                                           interpolation=cv2.INTER_NEAREST)[0, :]

        else:
            self.sensor_value = np.zeros((self.polar_view.shape[0]))

        self.apply_normalization()

    def apply_normalization(self):
        if self.normalize:

            self.sensor_value = self.sensor_value /(self._range - self._min_range)

    @property
    def shape(self):
        return self._resolution

    def draw(self, width_display, height_sensor):

        # pylint: disable=no-member

        expanded = np.zeros((self.shape, 3))
        for i in range(3):
            expanded[:, i] = self.sensor_value[:]
        img = np.expand_dims(expanded, 0)
        img = cv2.resize(img, (width_display, height_sensor), interpolation=cv2.INTER_NEAREST)

        if self.normalize is False: img /= (self._range - self._min_range)/(2.0*self._scale_ratio)


        return img
