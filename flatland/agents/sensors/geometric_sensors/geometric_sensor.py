from flatland.agents.sensors.sensor import *
from ....utils.definitions import SensorModality

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
