from collections import defaultdict

class LidarSensor():

    def __init__(self, anatomy, custom_config):

        self.sensor_type = 'lidar'
        sensor_param = { **custom_config}

        self.observation = None

        pass


    def update_sensor(self, current_agent, entities, agents):


        print(current_agent)
        #Current's agent Shape
        agent_shape = current_agent.frame.anatomy['base'].shape
        agent_position = agent_shape.body.position



        #Gathering Shapes of entities and agents, in sorted dict bi entity type
        sorted_shapes = dict()


        # TODO : ambiguité sur les shapes disponibles des entités.
        #pm interaction shape ? visible shape ? premier de pm elements ?
        for entity in entities:
            key = type(entity)
            if not key in sorted_shapes:
                sorted_shapes[key] = []

            #Looks like the relevant Pymunk shape is the last one
            #To check in entity.py
            relevant_pm_element = entity.pm_elements[-1]

            sorted_shapes[key].append(relevant_pm_element)

        for agent in agents:
            key = type(agent)
            if not key in sorted_shapes:
                sorted_shapes[key] = []
            sorted_shapes[key].append(agent.frame.anatomy["base"].shape)

        for entity_type, entity_shapes in sorted_shapes.items():

            #Tests on entity_type
            for shape in entity_shapes:
                print(shape.body.position)
                # print(shape.)
                # shape_position = shape.body.position
                # p = shape.segment_query(agent_position, shape_position)
                #print(p)
        pass



    def get_shape_observation(self):
        pass
