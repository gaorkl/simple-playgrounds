

class LidarSensor():

    def __init__(self, anatomy, custom_config):

        self.sensor_type = 'lidar'
        sensor_param = { **custom_config}

        self.observation = None

        pass


    def update_sensor(self, entities, agents):

        for entity in entities:
            print(entity.pm_body.position)

        for agent in agents:
            print(agent.frame)
        print("****************")

        pass



    def get_shape_observation(self):
        pass
