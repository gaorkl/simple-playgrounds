from flatland.agents.sensors.sensor import *
from flatland.agents.sensors.geometric_sensors.geometric_sensor import *
from collections import defaultdict
from pymunk.vec2d import Vec2d
import math


@SensorGenerator.register('lidar')
class LidarSensor(GeometricSensor):

    def __init__(self, anchor, custom_config):

        self.sensor_type = 'lidar'

        #Todo later: add default config, as in visual_sensors
        sensor_param = { **custom_config}

        super(LidarSensor, self).__init__(anchor, sensor_param)


        #Sensor paramters TODO: make it parametrable
        self.FoV = 100 #in pixels
        self.angle_ranges = [(0,90),(90,180),(180,270),(270,359)]

        self.cones_number = len(self.angle_ranges)
        self.observation = None


    def update_sensor(self, current_agent, entities, agents):


        #Initialising ouput
        output = [dict() for i in range(self.cones_number)]

        #Current's agent Shape
        agent_shape = self.anchor.pm_visible_shape
        agent_position = self.anchor.pm_body.position
        agent_angle = self.anchor.pm_body.angle

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

            #Value initialisation: initial activation = 0
            for i in range(self.cones_number):
                output[i][entity_type] = 0

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
                angle = angle + math.degrees(agent_angle) #Add agent angle to count for rotation
                angle = angle%360 #To avoid negative and angles > to 360
                cone = None

                for i in range(len(self.angle_ranges)):
                    angle_range = self.angle_ranges[i]

                    if angle >= angle_range[0] and angle < angle_range[1]:
                        cone = i

                if cone is None:
                    break


                if not entity_type in output[cone]:

                    output[cone][entity_type] = 0

                normalised_distance = distance/self.FoV
                activation = 1 - normalised_distance

                #Keeping only the nearest distance = highest activation
                if output[cone][entity_type] < activation:
                    output[cone][entity_type] = activation

        self.sensor_value = output

        return output



    def get_shape_observation(self):
        pass
