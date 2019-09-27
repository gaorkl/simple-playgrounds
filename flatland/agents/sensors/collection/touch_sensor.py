from flatland.agents.sensors.sensor import SensorGenerator, Sensor
import numpy as np
import cv2


@SensorGenerator.register('touch')
class TouchSensor(Sensor):

    def __init__(self, anatomy, sensor_param):

        sensor_param['fovRange'] = sensor_param['minRange'] + sensor_param['contactRange']
        super(TouchSensor, self).__init__(anatomy, sensor_param)


    def update_sensor(self, img ):

        super().update_sensor( img )

        # Get value sensor
        if np.sum( self.pixels_sensor) != 0:
            mask = self.pixels_sensor != 0
            sensor = np.min(np.where(mask.any(axis=1), mask.argmax(axis=1), self.pixels_sensor.shape[1] - 1), axis=1)

            self.observation = (self.pixels_sensor.shape[1] - sensor) / self.pixels_sensor.shape[1]

        else:
            self.observation = np.zeros( (self.pixels_sensor.shape[0] ))

    def get_shape_observation(self):
        return self.fovResolution, 3