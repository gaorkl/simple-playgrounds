from ..visual_sensor import VisualSensor

import numpy as np
import cv2


class DepthSensor(VisualSensor):

    sensor_type = 'depth'

    def __init__(self, anchor, invisible_elements, **kwargs):

        super(DepthSensor, self).__init__(anchor, invisible_elements, **kwargs)

    def update_sensor(self, img, entities, agents):

        super().update_sensor(img, None, None)

        mask = self.polar_view != 0
        sensor = np.min(np.where(mask.any(axis=1), mask.argmax(axis=1), self.polar_view.shape[1] - 1), axis=1)

        sensor_value = (self.polar_view.shape[1] - sensor) / self.polar_view.shape[1]

        im = np.asarray(sensor_value)
        im = np.expand_dims(im, 0)
        self.sensor_value = cv2.resize(im, (self.fovResolution, 1), interpolation=cv2.INTER_NEAREST)[0, :]

    def shape(self):
        return self.fovResolution,
