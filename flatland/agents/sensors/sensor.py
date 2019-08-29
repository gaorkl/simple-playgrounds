from abc import abstractmethod, ABC
import math
import cv2
import numpy as np

import time

class SensorGenerator:

    """
    Register class to provide a decorator that is used to go through the package and
    register available playgrounds.
    """

    subclasses = {}

    @classmethod
    def register(cls, sensor_type):
        def decorator(subclass):
            cls.subclasses[sensor_type] = subclass
            return subclass

        return decorator

    @classmethod
    def create(cls, anatomy, sensor_param ):

        sensor_type = sensor_param["type"]

        if sensor_type not in cls.subclasses:
            raise ValueError('Sensor not implemented:' + sensor_type)

        return cls.subclasses[sensor_type](anatomy, sensor_param )


def get_rotated_point(x_1, y_1, x_2, y_2, angle, height):
    # Rotate x_2, y_2 around x_1, y_1 by angle.
    x_change = (x_2 - x_1) * math.cos(angle) + \
               (y_2 - y_1) * math.sin(angle)
    y_change = (y_1 - y_2) * math.cos(angle) - \
               (x_1 - x_2) * math.sin(angle)
    new_x = x_change + x_1
    new_y = height - (y_change + y_1)
    return int(new_x), int(new_y)


class Sensor(ABC):

    def __init__(self, anatomy, sensor_param):

        self.name = sensor_param.get('name', None)

        # Field of View of the Sensor
        self.fovResolution = sensor_param.get('fovResolution', None)
        self.fovRange = sensor_param.get('fovRange', None)
        self.fovAngle = sensor_param.get('fovAngle', None)
        self.min_range = sensor_param.get('minRange', None)

        
        # Anchor of the sensor
        body_anchor = sensor_param.get('bodyAnchor', None)
        self.body_anchor = anatomy[body_anchor].body

        # Relative location (polar) and angle wrt body
        self.d_r = sensor_param.get('d_r', None)
        self.d_theta = sensor_param.get('d_theta', None)
        self.d_relativeOrientation = sensor_param.get('d_relativeOrientation', None)




        self.get_shape_observation()

        self.resized_img = None
        self.cropped_img = None

        self.observation = None

        self.bbox_initialized = False



    @abstractmethod
    def update_sensor(self, img):

        w, h, _ = img.shape

        t1 = time.time()

        # Position of the sensor
        sensor_x, sensor_y = self.body_anchor.position
        sensor_angle = self.body_anchor.angle + math.pi

        # # Crop area around agent early
        # rolled_img = np.roll(img, (int( w/2-sensor_y), int( h/2-sensor_x)) ,( 0,1 ))
        #
        # t2 = time.time()
        #
        # if not self.bbox_initialized:
        #
        #     # Prevent to crop outside of image
        #
        #     self.mid_w_bbox = min(w/2, self.fovRange+1)
        #     self.mid_h_bbox = min(h/2, self.fovRange+1)
        #
        #     # Opencv linerar polar crashes when image is too small
        #
        #     self.mid_w_bbox = int(max(self.mid_w_bbox, 80))
        #     self.mid_h_bbox = int(max(self.mid_h_bbox, 80))
        #     self.bbox_initialized = True
        #
        #
        # cropped_img = rolled_img[ int(w/2) - self.mid_w_bbox : int(w/2) + self.mid_w_bbox + 1,
        #               int(h / 2) - self.mid_h_bbox : int(h / 2) + self.mid_h_bbox + 1
        #               ]
        t3 = time.time()

        # polar_img = cv2.linearPolar(cropped_img, (self.mid_w_bbox, self.mid_h_bbox), self.fovRange  , flags=cv2.INTER_NEAREST)
        polar_img = cv2.linearPolar(img, (sensor_x, sensor_y), self.fovRange  , flags=cv2.INTER_NEAREST)

        t4 = time.time()

        angle_center = w * (sensor_angle % (2 * math.pi)) / (2 * math.pi)
        rolled_img = np.roll(polar_img, int( w - angle_center), axis=0)

        t5 = time.time()

        start_crop = int(self.min_range * h / self.fovRange)

        cropped_img = rolled_img[
                      int(w / 2 - w * (self.fovAngle / 2.0) / (2 * math.pi)):int(
                          w / 2 + w * (self.fovAngle / 2.0) / (2 * math.pi)) + 1,
                      start_crop:
                      ]

        t6 = time.time()

        resized_img = cv2.resize(
            cropped_img,
            (cropped_img.shape[1], int(self.fovResolution)),
            interpolation=cv2.INTER_NEAREST
        )

        t7 = time.time()

        self.resized_img = resized_img[::-1, :, ::-1]
        self.cropped_img = cropped_img[::-1, :, ::-1]

        t8 = time.time()

        print(self.name,  t4-t3, t5-t4, t6-t5, t7-t6, t8-t7 )

    # t2 - t1, t3 - t2,
    @abstractmethod
    def get_shape_observation(self):
        pass