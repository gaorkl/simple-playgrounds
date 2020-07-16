from ..sensor import Sensor
from flatland.utils.definitions import SensorModality

import math
from abc import abstractmethod
import os
import yaml

from operator import attrgetter


class SemanticSensor(Sensor):

    sensor_type = 'semantic'

    def __init__(self, anchor, invisible_elements, remove_occluded = True, allow_duplicates = False, **sensor_param):

        super().__init__(anchor, invisible_elements,  **sensor_param)

        self.sensor_modality = SensorModality.SEMANTIC

        self._range = sensor_param.get('range')
        self._angle = sensor_param.get('fov') * math.pi / 180

        self.remove_occluded = remove_occluded
        self.allow_duplicates = allow_duplicates

    @staticmethod
    def parse_configuration(key):
        if key is None:
            return {}

        fname = 'semantic_sensor_default.yml'

        __location__ = os.path.realpath(os.path.join(os.getcwd(), os.path.dirname(__file__)))
        with open(os.path.join(__location__, fname), 'r') as yaml_file:
            default_config = yaml.load(yaml_file)

        return default_config[key]

    @abstractmethod
    def update_sensor(self, pg):
        pass

    @property
    def shape(self):
        return 2*self._range, 2*self._range
