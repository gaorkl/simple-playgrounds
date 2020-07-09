from flatland.agents.sensors.sensor import *


class GeometricSensor(Sensor):

    sensor_type = 'geometric'

    def __init__(self, anchor, **sensor_param):

        super().__init__(anchor, **sensor_param )

        self.sensor_modality = SensorModality.GEOMETRIC


    @abstractmethod
    def update_sensor(self, current_agent, entities, agents):
        pass



    @abstractmethod
    def get_shape_observation(self):
        pass
