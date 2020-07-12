from abc import abstractmethod, ABC
import math


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

    index_sensor = 0
    sensor_type = 'sensor'

    def __init__(self, anchor, invisible_elements, **sensor_param):

        # Sensor name
        # Internal counter to assign number and name to each sensor
        self.name = sensor_param.get('name', self.sensor_type + '_' + str(Sensor.index_sensor))
        Sensor.index_sensor += 1

        # Anchor of the sensor
        self.anchor = anchor
        self.anchor_body = anchor.pm_body

        self.sensor_params = sensor_param
        self.sensor_value = None

        self.invisible_elements = invisible_elements

    @abstractmethod
    def update_sensor(self, img, entities, agents):
        pass

    @property
    @abstractmethod
    def shape(self):
        pass


