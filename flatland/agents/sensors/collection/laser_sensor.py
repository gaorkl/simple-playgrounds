from flatland.agents.sensors.sensor import SensorGenerator, Sensor
import numpy as np
import cv2
import math

@SensorGenerator.register('laser')
class LaserSensor(Sensor):

    def __init__(self, anatomy, sensor_param):


        self.angle_laser_point = sensor_param['laserPointAngle']
        self.number_laser_point = sensor_param['laserPointNumber']

        if self.number_laser_point < 1:
            raise ValueError('number_laser_point should be higher than 1')

        sensor_param['fovResolution'] = int(sensor_param['fovAngle'] / sensor_param['laserPointAngle'])

        super(LaserSensor, self).__init__(anatomy, sensor_param)

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
            self.observation = cv2.resize(im, (self.fovResolution, 1), interpolation=cv2.INTER_NEAREST)


            sensor = [ int(self.observation[0, index]*float(self.fovRange)/self.pixels_sensor.shape[1]) for index in self.index_sensors]

            #self.observation = (self.pixels_sensor.shape[1] - sensor) / self.pixels_sensor.shape[1]


            self.observation = sensor

        else:
            self.observation = np.zeros( (self.pixels_sensor.shape[0] ))

    def get_shape_observation(self):
        return self.fovResolution, 3