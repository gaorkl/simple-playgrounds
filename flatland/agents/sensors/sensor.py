from abc import abstractmethod, ABC
import math
import cv2
import numpy as np
import os, yaml
from enum import Enum, auto


class SensorModality(Enum):
    VISUAL      = auto()
    GEOMETRIC   = auto()
    UNDEFINED   = auto()


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
    def create(cls, sensor_type, anchor, invisible_body_parts, sensor_param):

        if sensor_type not in cls.subclasses:
            raise ValueError('Sensor not implemented:' + sensor_type)

        return cls.subclasses[sensor_type](anchor, invisible_body_parts, sensor_param )


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

    def __init__(self, anchor, invisible_entities, sensor_param):
        self.name = sensor_param.get('name', None)
        self.sensor_type = sensor_param.get('type', None)
        self.sensor_params = sensor_param
        self.sensor_modality = SensorModality.UNDEFINED
        self.sensor_value = None
        self.invisible_elements = invisible_entities


    @abstractmethod
    def update_sensor(self, entities, agents):
        pass

    @abstractmethod
    def get_shape_observation(self):
        pass


