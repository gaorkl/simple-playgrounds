from flatland.agents.sensors.sensor import *
from flatland.agents.sensors.geometric_sensors.geometric_sensor import *
from collections import defaultdict
from pymunk.vec2d import Vec2d
import math


class LidarSensor(GeometricSensor):

    def __init__(self, anchor, invisible_body_parts, **custom_config):

        self.sensor_type = 'lidar'

        #Todo later: add default config, as in visual_sensors
        sensor_param = { **custom_config}
        super(LidarSensor, self).__init__(anchor, invisible_body_parts, sensor_param)


        #Sensor paramters TODO: make it parametrable
        self.FoV = sensor_param.get('FoV',100) #in pixels
        self.angle_ranges = sensor_param.get('angle_ranges',[(0,90),(90,180),(180,270),(270,359)])

        self.cones_number = len(self.angle_ranges)
        self.observation = None


    def update_sensor(self, current_agent, entities, agents):


        #Initialising ouput
        output = [dict() for i in range(self.cones_number)]

        #Current's agent Shape
        agent_position = current_agent.position
        agent_coord = Vec2d(agent_position[0], agent_position[1])
        agent_angle = agent_position[2]

        #Gathering positions of entities and agents, in sorted dict by entity/agent type
        sorted_positions = dict()

        #Gathering key and shapes from entities
        for entity in entities:

            key = type(entity).__name__ #Key in matrix

            if not key in sorted_positions:
                sorted_positions[key] = []

            #Looks like the relevant Pymunk position is the last one
            #To check in entity.py
            sorted_positions[key].append(entity.position)

        #Gathering key and shapes from agents
        for agent in agents:
            key = type(agent).__name__ #Key in matrix
            if not key in sorted_positions:
                sorted_positions[key] = []

            #Agent shouldn't detect itself
            if not agent is current_agent:
                sorted_positions[key].append(agent.position)


        #For each entity type
        for entity_type, positions in sorted_positions.items():

            #add here: Tests on entity_type : can the entity be detected ?

            #Value initialisation: initial activation = 0
            for i in range(self.cones_number):
                output[i][entity_type] = 0

            #For each entity
            for position in positions:

                #Calculating the nearest point on the entity's surface
                #query = shape.segment_query(agent_coord, shape_position)
                #near_point = query.point


                #For debugging purpose
                #Approximation : center ph position instead of projection
                near_point = position

                #if entity_type == 'Candy':
                    #self.logger.add((position[0], position[1]),"near_point")
                    #self.logger.add((agent_position[0], agent_position[1]), "agent_position")


                #Distance check - is the object too far ?
                distance = agent_coord.get_distance(near_point)

                if distance > self.FoV:
                    continue

                #Angle check - In which cone does it fall ?
                dy = (near_point[1] - agent_coord[1])
                dx = (near_point[0] - agent_coord[0])
                target_angle = math.atan2(dy, dx)

                relative_angle = target_angle - agent_angle #Add agent angle to count for rotation

                #if entity_type == 'Candy':
                    #self.logger.add(relative_angle,"relative_angle")
                    #self.logger.add(target_angle,"target_angle")
                    #self.logger.add(agent_angle, "agent_angle")

                relative_angle_degrees =math.degrees(relative_angle)%360 #To avoid negative and angles > to 360
                cone = None

                #Calculating in which cone the position is detected
                for i in range(len(self.angle_ranges)):
                    angle_range = self.angle_ranges[i]

                    if relative_angle_degrees >= angle_range[0] and relative_angle_degrees < angle_range[1]:
                        cone = i

                if cone is None:
                    continue


                if not entity_type in output[cone]:

                    output[cone][entity_type] = 0

                normalised_distance = distance/self.FoV
                activation = 1 - normalised_distance



                #Keeping only the nearest distance = highest activation
                if output[cone][entity_type] < activation:
                    output[cone][entity_type] = activation
        self.observation = output

        return output

    def get_shape_observation(self):
        pass
