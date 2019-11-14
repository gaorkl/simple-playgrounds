from flatland.agents.sensors.sensor import SensorGenerator, Sensor
import numpy as np
import cv2
import time

@SensorGenerator.register('rgb')
class RgbSensor(Sensor):

    def __init__(self, anatomy, sensor_param):
        super(RgbSensor, self).__init__(anatomy, sensor_param)

    def update_sensor(self, img):

        super().update_sensor( img)

        # Get value sensor
        mask = self.pixels_sensor != 0
        sensor_id = np.min(np.where(mask.any(axis=1), mask.argmax(axis=1), self.pixels_sensor.shape[1] - 1), axis=1)
        
        self.observation = self.pixels_sensor[np.arange(int(self.fovResolution)), sensor_id, :]


    def get_shape_observation(self):

        return  self.fovResolution, 1, 3
