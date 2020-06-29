from flatland.agents.sensors.visual_sensors.visual_sensor import *

import numpy as np
import cv2


class RgbSensor(VisualSensor):

    sensor_type = 'rgb'

    def __init__(self, anchor, invisible_body_parts, **kwargs):

        super(RgbSensor, self).__init__(anchor, invisible_body_parts, **kwargs)

    def update_sensor(self, img):

        super().update_sensor( img )

        # Get value sensor
        mask = self.polar_view != 0
        sensor_id = np.min(np.where(mask.any(axis=1), mask.argmax(axis=1), self.polar_view.shape[1] - 1), axis=1)
        sensor_value = self.polar_view[np.arange(int(self.polar_view.shape[0])), sensor_id, :]

        im = np.asarray(sensor_value)
        im = np.expand_dims(im, 0)
        self.sensor_value = cv2.resize(im, (self.fovResolution, 1), interpolation=cv2.INTER_NEAREST)

    def get_shape_observation(self):

        return self.fovResolution, 1, 3


class GreySensor(RgbSensor):

    sensor_type = 'grey'

    def __init__(self, anchor, invisible_body_parts, **kwargs):
        super(RgbSensor, self).__init__(anchor, invisible_body_parts, **kwargs)

    def update_sensor(self, img):

        super().update_sensor(img)
        self.sensor_value = cv2.cvtColor(self.sensor_value, cv2.COLOR_BGR2GRAY)

    def get_shape_observation(self):
        return self.fovResolution, 1, 1
