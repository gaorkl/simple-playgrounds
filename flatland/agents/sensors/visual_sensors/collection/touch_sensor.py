from flatland.agents.sensors.visual_sensors.visual_sensor import *
import numpy as np
import cv2


class TouchSensor(VisualSensor):

    sensor_type = 'touch'

    def __init__(self, anchor, invisible_body_parts, **kwargs):

        super(TouchSensor, self).__init__(anchor, invisible_body_parts, min_range = anchor.radius,  **kwargs)

        self.fovRange = self.min_range + self.fovRange


    def update_sensor(self, img ):

        super().update_sensor( img )

        # Get value sensor
        if np.sum( self.polar_view) != 0:
            mask = self.polar_view != 0
            sensor = np.min(np.where(mask.any(axis=1), mask.argmax(axis=1), self.polar_view.shape[1] - 1), axis=1)

            sensor_value = (self.polar_view.shape[1] - sensor) / self.polar_view.shape[1]

            im = np.asarray(sensor_value)
            im = np.expand_dims(im, 0)
            self.sensor_value = cv2.resize(im, (self.fovResolution, 1), interpolation=cv2.INTER_NEAREST)

        else:
            self.sensor_value = np.zeros( (self.polar_view.shape[0] ))

    def get_shape_observation(self):
        return self.fovResolution, 3
