from flatland.agents.sensors.visual_sensors.visual_sensor import *
import numpy as np
import cv2


class DistanceArraySensor(VisualSensor):

    sensor_type = 'distance_array'

    def __init__(self, anchor, invisible_body_parts, **kwargs):

        default_config = self.parse_configuration(self.sensor_type)
        sensor_params = {**default_config, **kwargs}

        self.angle_laser_point = sensor_params['point_angle']
        self.number_laser_point = sensor_params['number']

        if self.number_laser_point < 1:
            raise ValueError('number_laser_point should be higher than 1')

        res= int(sensor_params['fov'] / sensor_params['point_angle'])

        super(DistanceArraySensor, self).__init__(anchor, invisible_body_parts, resolution = res,  **kwargs)

        self.index_sensors = []
        for i in range(self.number_laser_point):
            index = int( i * ((self.fovResolution-1) / (self.number_laser_point - 1)) )
            self.index_sensors.append( index )

    def update_sensor(self, img):

        super().update_sensor( img )

        mask = self.polar_view != 0
        sensor = np.min(np.where(mask.any(axis=1), mask.argmax(axis=1), self.polar_view.shape[1] - 1), axis=1)

        im = np.asarray(sensor)
        im = np.expand_dims(im, 0)
        sensor_value = cv2.resize(im, (self.fovResolution, 1), interpolation=cv2.INTER_NEAREST)

        sensor_value = [ 1+ int(sensor_value[0, index]*float(self.fovRange)/self.polar_view.shape[1]) for index in self.index_sensors]

        self.sensor_value = sensor_value


    def get_shape_observation(self):
        return self.number_laser_point, 1
