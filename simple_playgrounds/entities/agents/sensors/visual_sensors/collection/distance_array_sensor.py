"""
Module defining Distance Array Sensor
"""
import numpy as np
import cv2

from simple_playgrounds.entities.agents.sensors.visual_sensors.visual_sensor import VisualSensor

# pylint: disable=no-member


class DistanceArraySensor(VisualSensor):
    """
    Distance Array Sensor calculates the distance of obstacles along Cones.
    """
    sensor_type = 'distance_array'

    def __init__(self, anchor, invisible_elements=None, normalize=True, **kwargs):
        """
        Args:
            anchor: body Part to which the sensor is attached.
                Sensor is attached to the center of the Part.
            invisible_elements: elements that the sensor does not perceive.
                List of Parts of SceneElements.
            normalize: if true, Sensor values are normalized between 0 and 1.

        Keyword Args:
            point_angle: angle of opening of the Cone.
            number: number of cones.
        """

        default_config = self.parse_configuration(self.sensor_type)
        sensor_params = {**default_config, **kwargs}

        self._angle_laser_point = sensor_params['point_angle']
        self._number_laser_point = sensor_params['number']

        if self._number_laser_point < 1:
            raise ValueError('number_laser_point should be higher than 1')

        res = int(sensor_params['fov'] / sensor_params['point_angle'])

        super().__init__(anchor, invisible_elements, normalize=normalize, resolution=res, **kwargs)

        self.index_sensors = []
        for i in range(self._number_laser_point):
            index = int(i * ((self._resolution - 1) / (self._number_laser_point - 1)))
            self.index_sensors.append(index)

        self._value_range = self._range

    def update_sensor(self, img):

        super().update_sensor(img)

        mask = self.polar_view != 0
        sensor = np.min(np.where(mask.any(axis=1), mask.argmax(axis=1), self.polar_view.shape[1]-1),
                        axis=1)

        image = np.asarray(sensor)
        image = np.expand_dims(image, 0)
        sensor_value = cv2.resize(image, (self._resolution, 1), interpolation=cv2.INTER_NEAREST)

        sensor_value = [1+int(sensor_value[0, index]*float(self._range)/self.polar_view.shape[1])
                        for index in self.index_sensors]

        self.sensor_value = np.asarray(sensor_value)

        self.apply_normalization()

    def apply_normalization(self):

        if self.normalize:
            self.sensor_value = self.sensor_value*1.0/self._range

    @property
    def shape(self):
        return self._number_laser_point

    def draw(self, width_display, height_sensor):

        expanded = np.zeros((self.shape, 3))
        for i in range(3):
            expanded[:, i] = self.sensor_value[:]
        img = np.expand_dims(expanded, 0)
        img = cv2.resize(img, (width_display, height_sensor), interpolation=cv2.INTER_NEAREST)

        if self.apply_normalization is False:
            img *= 1.0/self._range

        return img
