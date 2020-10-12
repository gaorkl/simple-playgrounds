"""
Module defining Geometric Sensors, that return distance to object detected.
"""
import math
from abc import ABC
import os
import yaml

import numpy as np
import cv2

from simple_playgrounds.entities.agents.sensors.sensor import Sensor
from simple_playgrounds.utils.definitions import SensorModality


class GeometricSensor(Sensor, ABC):
    """
    Base class for semantic sensors.
    Refer to base class Sensor.
    """
    sensor_modality = SensorModality.GEOMETRIC

    sensor_type = 'semantic'

    def __init__(self, anchor, invisible_elements=None, normalize=False, **sensor_param):

        super().__init__(anchor, invisible_elements, **sensor_param)

        self.range = sensor_param.get('range')
        self._fov = sensor_param.get('fov') * math.pi / 180
        self._resolution = sensor_param.get('resolution')

        self.normalize = normalize

    @staticmethod
    def _parse_configuration(key):
        if key is None:
            return {}

        fname = 'geometric_sensor_default.yml'

        __location__ = os.path.realpath(os.path.join(os.getcwd(), os.path.dirname(__file__)))
        with open(os.path.join(__location__, fname), 'r') as yaml_file:
            default_config = yaml.load(yaml_file, Loader=yaml.FullLoader)

        return default_config[key]

    def apply_noise(self):
        pass

    def update_sensor(self, env):

        self.compute_raw_sensor(env)

        if self.normalize:
            self.apply_normalization()

    @property
    def shape(self):
        return self._resolution
