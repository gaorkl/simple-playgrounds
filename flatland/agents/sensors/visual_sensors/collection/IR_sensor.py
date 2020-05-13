from flatland.agents.sensors.visual_sensors.visual_sensor import *
import numpy as np
import cv2
import os, yaml

__location__ = os.path.realpath(os.path.join(os.getcwd(), os.path.dirname(__file__)))
with open(os.path.join(__location__, 'sensor_default.yml'), 'r') as yaml_file:
    default_config = yaml.load(yaml_file)


@SensorGenerator.register('infra-red')
class InfraRedSensor(VisualSensor):

    def __init__(self, anatomy, sensor_param):


        sensor_param = {**default_config['infra-red'], **sensor_param}

        self.angle_laser_point = sensor_param['point_angle']
        self.number_laser_point = sensor_param['number']

        if self.number_laser_point < 1:
            raise ValueError('number_laser_point should be higher than 1')

        sensor_param['resolution'] = int(sensor_param['fov'] / sensor_param['point_angle'])

        super(InfraRedSensor, self).__init__(anatomy, sensor_param)

        self.index_sensors = []
        for i in range(self.number_laser_point):
            index = int( i * ((self.fovResolution-1) / (self.number_laser_point - 1)) )
            self.index_sensors.append( index )

    def update_sensor(self, img ):

        super().update_sensor( img )

        # Get value sensor
        if np.sum( self.pixels_sensor) != 0:
            mask = self.pixels_sensor != 0
            sensor = np.min(np.where(mask.any(axis=1), mask.argmax(axis=1), self.pixels_sensor.shape[1] - 1), axis=1)

            im = np.asarray(sensor)
            im = np.expand_dims(im, 0)
            sensor_value = cv2.resize(im, (self.fovResolution, 1), interpolation=cv2.INTER_NEAREST)

            sensor_value = [ int(sensor_value[0, index]*float(self.fovRange)/self.pixels_sensor.shape[1]) for index in self.index_sensors]

            #self.observation = (self.pixels_sensor.shape[1] - sensor) / self.pixels_sensor.shape[1]


            self.sensor_value = sensor

        else:
            self.observation = np.zeros( (self.pixels_sensor.shape[0] ))

    def get_shape_observation(self):
        return self.fovResolution, 3
