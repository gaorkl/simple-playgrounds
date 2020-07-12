from flatland.entities.agents.sensors.visual_sensors.visual_sensor import VisualSensor
import numpy as np
import cv2


class TopdownSensor(VisualSensor):

    sensor_type = 'topdown'

    def __init__(self, anchor, invisible_elements, only_front = False, **kwargs):

        super(TopdownSensor, self).__init__(anchor, invisible_elements, **kwargs)

        self.only_front = only_front

    def update_sensor(self, img, entities, agents ):

        w, h, _ = img.shape

        # Position of the sensor
        sensor_x, sensor_y = self.anchor_body.position
        sensor_x, sensor_y = int(sensor_x), int(sensor_y)
        sensor_angle = (math.pi / 2 - self.anchor_body.angle)

        mask_total_fov = np.zeros((w, h, 3))
        center = h - int(sensor_y), w - int(sensor_x)
        # cv2.circle(mask_total_fov, center, self.fovRange, (255, 255, 255), thickness=-1)

        mask_total_fov = cv2.ellipse(mask_total_fov, center, axes=(self.fovRange, self.fovRange), angle=0,
                    startAngle= (math.pi + sensor_angle-self.fovAngle/2)*180/math.pi,
                    endAngle=(math.pi + sensor_angle+self.fovAngle/2)*180/math.pi,
                    color = (1, 1, 1), thickness=-1)#, lineType=8, shift=0)

        masked_img = mask_total_fov * img

        x_start_crop =  int(max(0, center[1] - self.fovRange))
        x_end_crop = int(min(w, center[1] + self.fovRange))

        y_start_crop = int(max(0, center[0] - self.fovRange))
        y_end_crop = int(min(h, center[0] + self.fovRange))


        extended_cropped = np.zeros(((2*self.fovRange + 1), (2*self.fovRange + 1), 3))

        extended_cropped[self.fovRange  -(center[1] - x_start_crop):self.fovRange + (x_end_crop - center[1]) ,
                            self.fovRange  - (center[0] - y_start_crop):self.fovRange + (y_end_crop - center[0]) ,:]\
            = masked_img[x_start_crop:x_end_crop,y_start_crop:y_end_crop,:]
        #

        image_center = tuple(np.array(extended_cropped.shape[1::-1]) / 2)
        rot_mat = cv2.getRotationMatrix2D(image_center, sensor_angle*180/math.pi - 90, 1.0)
        result = cv2.warpAffine(extended_cropped, rot_mat, extended_cropped.shape[1::-1], flags=cv2.INTER_NEAREST)

        if self.only_front:
            result = result[:self.fovRange, :, :]
            self.sensor_value = cv2.resize(result, ( 2*self.fovResolution, self.fovResolution), interpolation=cv2.INTER_NEAREST)
        else:
            self.sensor_value = cv2.resize(result, ( 2*self.fovResolution, 2*self.fovResolution), interpolation=cv2.INTER_NEAREST)

        self.sensor_value /= 255.


    def shape(self):

        if self.only_front:
            return self.fovResolution, 2*self.fovResolution, 3

        else:
            return 2*self.fovResolution, 2*self.fovResolution, 3
