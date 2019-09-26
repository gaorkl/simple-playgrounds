from abc import abstractmethod, ABC
import math
import cv2
import numpy as np


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
        self.min_range = sensor_param.get('minRange', 0)

        
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

        pixels_per_degrees = self.fovResolution / ( 360 *  self.fovAngle / (2*math.pi ) )

        self.w_projection_img = int(360*pixels_per_degrees)


    @abstractmethod
    def update_sensor(self, img):

        w, h, _ = img.shape

        # Position of the sensor
        sensor_x, sensor_y = self.body_anchor.position
        sensor_angle = self.body_anchor.angle + math.pi

        img_resized_fov = cv2.resize( img, (img.shape[1], self.w_projection_img), interpolation=cv2.INTER_NEAREST )

        center_agent = ( sensor_x, sensor_y * self.w_projection_img / w)

        #print( img_resized_fov.shape)
        polar_img = cv2.linearPolar(img_resized_fov, center_agent, self.fovRange, flags=cv2.INTER_NEAREST)

        angle_center =  self.w_projection_img * (sensor_angle % (2 * math.pi)) / (2 * math.pi)
        rolled_img = np.roll(polar_img, int( self.w_projection_img - angle_center), axis=0)

        start_crop = int(self.min_range * h / self.fovRange)
        #end_crop = self.fovRange# min( int(self.fovRange), h)

        cropped_img = rolled_img[
                      int(self.w_projection_img / 2 - self.w_projection_img * (self.fovAngle / 2.0) / (2 * math.pi)):
                      int( self.w_projection_img / 2 + self.w_projection_img * (self.fovAngle / 2.0) / (2 * math.pi)) + 1,
                      start_crop:
                      ]

        resized_img = cv2.resize(
            cropped_img,
            (cropped_img.shape[1], int(self.fovResolution)),
            interpolation=cv2.INTER_NEAREST
        )


        self.resized_img = resized_img[::-1, :, ::-1]/255.0
        self.cropped_img = cropped_img[::-1, :, ::-1]/255.0

    @abstractmethod
    def get_shape_observation(self):
        pass