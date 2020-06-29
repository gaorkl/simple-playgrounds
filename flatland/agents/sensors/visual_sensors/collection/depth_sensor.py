from flatland.agents.sensors.visual_sensors.visual_sensor import *
import numpy as np
import cv2


class DepthSensor(VisualSensor):

    sensor_type = 'depth'

    def __init__(self, anchor, invisible_body_parts, **kwargs):

        super(DepthSensor, self).__init__(anchor, invisible_body_parts, **kwargs)

    def update_sensor(self, img ):

        super().update_sensor( img)

        mask = self.polar_view != 0
        sensor = np.min(np.where(mask.any(axis=1), mask.argmax(axis=1), self.polar_view.shape[1] - 1), axis=1)

        sensor_value = (self.polar_view.shape[1] - sensor) / self.polar_view.shape[1]

        im = np.asarray(sensor_value)
        im = np.expand_dims(im, 0)
        self.sensor_value = cv2.resize(im, (self.fovResolution, 1), interpolation=cv2.INTER_NEAREST)



    def get_shape_observation(self):
        return self.fovResolution, 1
