from flatland.entities.agents.sensors.visual_sensors.visual_sensor import VisualSensor

import numpy as np
import cv2


class RgbSensor(VisualSensor):

    sensor_type = 'rgb'

    def __init__(self, anchor,invisible_elements, **kwargs):

        super(RgbSensor, self).__init__(anchor, invisible_elements, **kwargs)

    def update_sensor(self, img, entities, agents):

        super().update_sensor(img, None, None)

        # Get value sensor
        mask = self.polar_view != 0
        sensor_id = np.min(np.where(mask.any(axis=1), mask.argmax(axis=1), self.polar_view.shape[1] - 1), axis=1)
        sensor_value = self.polar_view[np.arange(int(self.polar_view.shape[0])), sensor_id, :]

        im = np.asarray(sensor_value)
        im = np.expand_dims(im, 0)
        self.sensor_value = cv2.resize(im, (self.fovResolution,1), interpolation=cv2.INTER_NEAREST)[0, :]

    def shape(self):

        return self.fovResolution, 3


class GreySensor(RgbSensor):

    sensor_type = 'grey'

    def __init__(self, anchor, invisible_elements, **kwargs):
        super(RgbSensor, self).__init__(anchor, invisible_elements, **kwargs)

    def update_sensor(self, img, entities, agents):

        super().update_sensor(img, None, None)

        self.sensor_value = np.expand_dims(self.sensor_value, 0)
        self.sensor_value = cv2.cvtColor(self.sensor_value, cv2.COLOR_BGR2GRAY)
        self.sensor_value = cv2.resize(self.sensor_value, (self.fovResolution, 1), interpolation=cv2.INTER_NEAREST)[0, :]



    def shape(self):
        return self.fovResolution,
