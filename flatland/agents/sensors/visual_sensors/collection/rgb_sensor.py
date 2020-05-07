from flatland.agents.sensors.visual_sensors.visual_sensor import *
import numpy as np
import cv2
import os, yaml

__location__ = os.path.realpath(os.path.join(os.getcwd(), os.path.dirname(__file__)))
with open(os.path.join(__location__, 'sensor_default.yml'), 'r') as yaml_file:
    default_config = yaml.load(yaml_file)


@SensorGenerator.register('rgb')
class RgbSensor(VisualSensor):

    def __init__(self, anatomy, sensor_param):

        sensor_param = {**default_config['rgb'], **sensor_param}

        super(RgbSensor, self).__init__(anatomy, sensor_param)

    def update_sensor(self, img):

        super().update_sensor( img)

        # Get value sensor
        mask = self.pixels_sensor != 0
        sensor_id = np.min(np.where(mask.any(axis=1), mask.argmax(axis=1), self.pixels_sensor.shape[1] - 1), axis=1)
        self.observation = self.pixels_sensor[np.arange(int(self.pixels_sensor.shape[0])), sensor_id, :]

        im = np.asarray(self.observation)
        im = np.expand_dims(im, 0)
        self.observation = cv2.resize(im, (self.fovResolution, 1), interpolation=cv2.INTER_NEAREST)




    def get_shape_observation(self):

        return  self.fovResolution, 1, 3
