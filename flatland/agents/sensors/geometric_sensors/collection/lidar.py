from flatland.agents.sensors.sensor import *
from flatland.agents.sensors.geometric_sensors.geometric_sensor import *
from collections import defaultdict
from pymunk.vec2d import Vec2d


@SensorGenerator.register('lidar')
class LidarSensor(GeometricSensor):

    def __init__(self, anatomy, custom_config):

        self.sensor_type = 'lidar'

        #Todo later: add default config, as in visual_sensors
        sensor_param = { **custom_config}

        super(LidarSensor, self).__init__(anatomy, sensor_param)


        #Sensor paramters TODO: make it parametrable
        self.FoV = 100 #in pixels
        self.angles = [-180, -90, 0, 90, 180]
        self.cones_number = len(self.angles)-1


    def update_sensor(self, current_agent, entities, agents):


        #Initialising ouput
        output = [dict() for i in range(self.cones_number)]

        #Current's agent Shape
        agent_shape = current_agent.frame.anatomy['base'].shape
        agent_position = agent_shape.body.position
        agent_angle = agent_shape.body.angle

        #Gathering Shapes of entities and agents, in sorted dict bi entity type
        sorted_shapes = dict()


        # TODO : ambiguité sur les shapes disponibles des entités.
        #pm interaction shape ? visible shape ? premier de pm elements ?
        for entity in entities:

            #key = type(entity)
            key = entity.__class__ #for dev purpose

            if not key in sorted_shapes:
                sorted_shapes[key] = []

            #Looks like the relevant Pymunk shape is the last one
            #To check in entity.py
            relevant_pm_element = entity.pm_elements[1]

            sorted_shapes[key].append(relevant_pm_element)

        for agent in agents:
            key = type(agent)
            if not key in sorted_shapes:
                sorted_shapes[key] = []

            #Agent shouldn't detect itself
            if not agent is current_agent:
                sorted_shapes[key].append(agent.frame.anatomy["base"].shape)


        #For each entity type
        for entity_type, entity_shapes in sorted_shapes.items():

            #add here: Tests on entity_type : can the entity be detected ?


            for i in range(self.cones_number):
                output[i][entity_type] = 1

            #For each entity
            for shape in entity_shapes:

                shape_position = shape.body.position
                shape_angle    = shape.body.angle

                #Calculating the nearest point on the entity's surface
                query = shape.segment_query(agent_position, shape_position)
                near_point = query.point

                #Distance check
                distance = agent_position.get_distance(near_point)

                if distance > self.FoV:
                    break

                #Angle check - In which cone does it fall ?
                angle = agent_position.get_angle_degrees_between(near_point) #in degrees
                cone = None

                for i in range(len(self.angles)-2):
                    if angle >= self.angles[i] and angle < self.angles[i+1]:
                        cone = i

                if cone is None:
                    break

                output[cone] = dict()

                if not entity_type in output[cone]:

                    output[cone][entity_type] = 1

                normalised_distance = distance/self.FoV

                #Keeping only the nearest distance
                if output[cone][entity_type] > normalised_distance:
                    output[cone][entity_type] = normalised_distance

        self.sensor_value = output

        return output



    def get_shape_observation(self):
        pass
