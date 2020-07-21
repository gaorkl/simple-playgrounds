"""
Module defining Semantic Sensors, that return Entities object detected.
"""
import math
from abc import abstractmethod
import os
import yaml

import numpy as np
import cv2

from simple_playgrounds.entities.agents.sensors.sensor import Sensor
from simple_playgrounds.utils.definitions import SensorModality


class SemanticSensor(Sensor):
    """
    Base class for semantic sensors.
    Refer to base class Sensor.
    """
    sensor_type = 'semantic'

    def __init__(self, anchor, invisible_elements=None, remove_occluded=True, allow_duplicates=False, **sensor_param):

        super().__init__(anchor, invisible_elements, **sensor_param)

        self.sensor_modality = SensorModality.SEMANTIC

        self._range = sensor_param.get('range')
        self._angle = sensor_param.get('fov') * math.pi / 180

        self.remove_occluded = remove_occluded
        self.allow_duplicates = allow_duplicates

    @staticmethod
    def _parse_configuration(key):
        if key is None:
            return {}

        fname = 'semantic_sensor_default.yml'

        __location__ = os.path.realpath(os.path.join(os.getcwd(), os.path.dirname(__file__)))
        with open(os.path.join(__location__, fname), 'r') as yaml_file:
            default_config = yaml.load(yaml_file, Loader=yaml.FullLoader)

        return default_config[key]

    @abstractmethod
    def update_sensor(self, pg):
        pass

    @property
    def shape(self):
        return 2*self._range, 2*self._range

    def draw(self, width_display, height_sensor):

        height_semantic = width_display

        img = np.zeros((height_semantic, width_display, 3))

        for angle, points in self.sensor_value.items():

            for point in points:
                distance = point.distance * height_semantic / self.shape[0]

                pos_x = int(height_semantic / 2 - distance * math.cos(angle))
                pos_y = int(height_semantic / 2 - distance * math.sin(angle))

                # pylint: disable=no-member
                cv2.circle(img, (pos_y, pos_x), 2, [0.1, 0.5, 1.0], thickness=-1)

        return img
