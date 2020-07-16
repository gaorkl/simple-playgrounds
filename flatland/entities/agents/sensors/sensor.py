"""
Module defining the Base Class for Sensors
"""
from abc import abstractmethod, ABC


class Sensor(ABC):
    """
    Base class Sensor.

    Attributes:
        anchor: body Part to which the sensor is attached.
            Sensor is attached to the center of the Part.
        sensor_value: values of the sensor.
        invisible_elements: elements that the sensor does not perceive. List of Parts of SceneElements.
        name: Name of the sensor.

    """

    index_sensor = 0
    sensor_type = 'sensor'

    def __init__(self, anchor, invisible_elements, **sensor_param):

        # Sensor name
        # Internal counter to assign number and name to each sensor
        self.name = sensor_param.get('name', self.sensor_type + '_' + str(Sensor.index_sensor))
        Sensor.index_sensor += 1

        # Anchor of the sensor
        self.anchor = anchor

        # self.sensor_params = sensor_param
        self.sensor_value = None

        self.invisible_elements = invisible_elements

    @abstractmethod
    def update_sensor(self):
        """ Updates the sensor"""

    @property
    @abstractmethod
    def shape(self):
        """ Returns the shape of the numpy array, if applicable."""
