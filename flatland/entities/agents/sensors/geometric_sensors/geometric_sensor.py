from flatland.entities.agents.sensors.sensor import Sensor
from flatland.utils.definitions import SensorModality
from abc import abstractmethod

class GeometricSensor(Sensor):

    sensor_type = 'geometric'

    def __init__(self, anchor, invisible_elements, **sensor_param):

        super().__init__(anchor, invisible_elements, **sensor_param )

        self.sensor_modality = SensorModality.GEOMETRIC


    @abstractmethod
    def update_sensor(self, img, entities, agents):
        pass


    @abstractmethod
    def shape(self):
        pass
