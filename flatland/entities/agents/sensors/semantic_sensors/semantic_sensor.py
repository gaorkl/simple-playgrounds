from ..sensor import Sensor
from flatland.utils.definitions import SensorModality

from abc import abstractmethod
import os
import yaml

from operator import attrgetter


class SemanticSensor(Sensor):

    sensor_type = 'semantic'

    def __init__(self, anchor, invisible_elements, remove_occluded = True, allow_duplicates = False, **sensor_param):

        super().__init__(anchor, invisible_elements, **sensor_param)

        self.sensor_modality = SensorModality.SEMANTIC

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

    @abstractmethod
    def shape(self):
        pass

    def filter_sensor_values(self):

        if self.remove_occluded:

            for angle, points in self.sensor_value.items():

                if points != []:
                    min_distance_point = min(points, key=attrgetter('distance'))
                    self.sensor_value[angle] = [min_distance_point]

                else:
                    self.sensor_value[angle] = []

        if not self.allow_duplicates:

            unique_points = {}
            all_points = []

            for angle, points in self.sensor_value.items():
                all_points += points

            for point in all_points:
                min_distance_point = min([pt for pt in all_points if pt.entity is point.entity],
                                         key=attrgetter('distance'))

                unique_points[min_distance_point.angle] = [min_distance_point]

            self.sensor_value = unique_points

