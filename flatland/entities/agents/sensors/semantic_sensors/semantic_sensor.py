from ..sensor import Sensor
from flatland.utils.definitions import SensorModality

from abc import abstractmethod
import os
import yaml


class SemanticSensor(Sensor):

    sensor_type = 'semantic'

    def __init__(self, anchor, invisible_elements, **sensor_param):

        super().__init__(anchor, invisible_elements, **sensor_param)

        self.sensor_modality = SensorModality.SEMANTIC

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

    @abstractmethod
    def shape(self):
        pass
