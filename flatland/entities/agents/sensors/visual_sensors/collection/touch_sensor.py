from flatland.entities.agents.sensors.visual_sensors.visual_sensor import VisualSensor
import numpy as np
import cv2


class TouchSensor(VisualSensor):

    sensor_type = 'touch'

    def __init__(self, anchor, invisible_elements, **kwargs):

        super(TouchSensor, self).__init__(anchor, invisible_elements, min_range = anchor.radius,  **kwargs)

        self.fovRange = self.min_range + self.fovRange

    def update_sensor(self, img, entities, agents ):

        super().update_sensor( img, None, None )

        # Get value sensor
        if np.sum( self.polar_view) != 0:
            mask = self.polar_view != 0
            sensor = np.min(np.where(mask.any(axis=1), mask.argmax(axis=1), self.polar_view.shape[1] - 1), axis=1)

            sensor_value = (self.polar_view.shape[1] - sensor) / self.polar_view.shape[1]

            im = np.asarray(sensor_value)
            im = np.expand_dims(im, 0)
            # im = np.expand_dims(im, -1)
            self.sensor_value = cv2.resize(im, (self.fovResolution, 1), interpolation=cv2.INTER_NEAREST)[0,  :]

        else:
            self.sensor_value = np.zeros( (self.polar_view.shape[0] ))

    def shape(self):
        return self.fovResolution,
