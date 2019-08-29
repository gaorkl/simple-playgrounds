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
        mask = self.resized_img != 0
        sensor = np.min(np.where(mask.any(axis=1), mask.argmax(axis=1), self.cropped_img.shape[1] - 1), axis=1)



        self.observation = (self.cropped_img.shape[1] - sensor) / self.cropped_img.shape[1]


    def get_shape_observation(self):
        return self.fovResolution, 3