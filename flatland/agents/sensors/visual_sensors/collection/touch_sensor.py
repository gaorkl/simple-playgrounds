from flatland.agents.sensors.visual_sensors.visual_sensor import *
import numpy as np
import cv2
import os, yaml

__location__ = os.path.realpath(os.path.join(os.getcwd(), os.path.dirname(__file__)))
with open(os.path.join(__location__, 'sensor_default.yml'), 'r') as yaml_file:
    default_config = yaml.load(yaml_file)


@SensorGenerator.register('touch')
class TouchSensor(VisualSensor):

    def __init__(self, anatomy, sensor_param):


        sensor_param = {**default_config['touch'], **sensor_param}

        sensor_param['range'] = sensor_param['minRange'] + sensor_param['contact_range']

        super(TouchSensor, self).__init__(anatomy, sensor_param)


    def update_sensor(self, img ):

        super().update_sensor( img )

        # Get value sensor
        if np.sum( self.pixels_sensor) != 0:
            mask = self.pixels_sensor != 0
            sensor = np.min(np.where(mask.any(axis=1), mask.argmax(axis=1), self.pixels_sensor.shape[1] - 1), axis=1)

            self.observation = (self.pixels_sensor.shape[1] - sensor) / self.pixels_sensor.shape[1]

            im = np.asarray(self.observation)
            im = np.expand_dims(im, 0)
            self.observation = cv2.resize(im, (self.fovResolution, 1), interpolation=cv2.INTER_NEAREST)

        else:
            self.observation = np.zeros( (self.pixels_sensor.shape[0] ))

    def get_shape_observation(self):
        return self.fovResolution, 3
