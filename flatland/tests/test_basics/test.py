from flatland.tests.test_basics.entities_pg import *
from flatland.tests.test_basics.test_pg import *
from flatland.entities.agents.basic_agents import *
from flatland.controllers.controller import Keyboard, Random
from flatland.entities.agents.sensors.visual_sensors import *
from flatland.entities.agents.sensors.semantic_sensors.lidar import *

# from flatland.agents.body_parts.body_part import BodyBase

pg = Basic_01()
# pg = Contact_01()
# pg = PositionObject_01()
# pg = Empty_01()
# pg = Doors_01()
# pg = Zones_01()
# pg = Proximity_01()
# pg = Trajectory_01()
# pg = Fields_01()
# pg = Interactive_01()
# pg = Conditioning_01()
# pg = Overlap()
# pg = NoOverlap()
# pg = Empty_Color_01()
# pg = Edibles_01()
agents = []

initial_position = PositionAreaSampler(area_shape='circle', center=[50 , 50], radius=10)
my_agent = BaseAgent(name = 'test_agent', initial_position=initial_position)
# my_agent = HeadAgent(name = 'test_agent', initial_position=initial_position)
# my_agent = HeadEyeAgent(initial_position=initial_position)
# my_agent = ArmAgent(initial_position=initial_position)
# my_agent = ArmHandAgent(initial_position=initial_position)

# controller = Random(available_actions=my_agent.get_all_available_actions())
controller = Keyboard(available_actions=my_agent.get_all_available_actions(), key_mapping= my_agent.key_mapping)
my_agent.assign_controller(controller)
agents.append(my_agent)


#
# other_agent = BaseAgent([250, 250, 0])
# controller = Random(available_actions=other_agent.get_all_available_actions())
# other_agent.assign_controller(controller)
# agents.append(other_agent)

# Add sensors:

# sensor = RgbSensor(name='rgb_1', anchor= my_agent.base_platform, invisible_elements=my_agent.body_parts, resolution=128, range=300)
sensor = TouchSensor(name='touch_1', anchor= my_agent.base_platform, invisible_elements=my_agent.body_parts)
# sensor = GreySensor(name='grey_1', anchor= my_agent.base_platform, invisible_elements=my_agent.body_parts)
# sensor = DepthSensor(name='depth_1', anchor= my_agent.base_platform, invisible_elements=my_agent.body_parts)
# sensor = DistanceArraySensor(name='test_1', anchor= my_agent.base_platform, invisible_elements=my_agent.body_parts,
#                              fov= 250,range = 400, number=1080)
# sensor = TopdownSensor(name='td_1', anchor= my_agent.base_platform, invisible_elements=my_agent.body_parts, range = 200, only_front = True)
#
# sensor = LidarCones(name='lidar', anchor=my_agent.base_platform,
#                    invisible_elements=my_agent.body_parts, fov=90, number_cones=10, range=300,
#                    remove_occluded=True, allow_duplicates=False)

my_agent.add_sensor(sensor)
#
#

# other_agent_1 = ArmAgent(name = 'agent_test_1', initial_position = [100, 300,0])
# controller_1 =  ()
# other_agent_1.assign_controller(controller_1)
# sensor_1 = RgbSensor(name='rgb_1', anchor= other_agent_1.base, invisible_body_parts=other_agent_1.body_parts, resolution = 128, range=100)
# other_agent_1.add_sensor(sensor_1)
# agents.append(other_agent_1)
#
# other_agent_2 = ArmHandAgent(name = 'agent_test_2', initial_position = [100, 200, 0.5])
# controller_2 = Random()
# other_agent_2.assign_controller(controller_2)
# sensor_2 = RgbSensor(name='rgb_3', anchor= other_agent_2.base, invisible_body_parts=other_agent_2.body_parts, resolution = 128, range=100)
# other_agent_2.add_sensor(sensor)
# agents.append(other_agent_2)
#
#
# for part in my_agent.body_parts:
#     print(my_agent.name, part.name, part.part_number)

# for part in other_agent_1.body_parts:
#     print(part.name, part.part_number, part.pm_visible_shape.filter )
#
# for part in other_agent_2.body_parts:
#     print(part.name, part.part_number, part.pm_visible_shape.filter )

# my_agent = agent.Agent('forward', name = 'mercotte',
#                        controller_type = 'keyboard',
#                        frame = { 'base': {'radius' : 10}},
#                        position=initial_position)


#my_agent.add_sensor('depth', 'depth_1', resolution = 128)
#my_agent.add_sensor('rgb', 'rgb_1', resolution = 128, fov = 90)
# my_agent.add_sensor('rgb', 'rgb_2', resolution = 128)
# my_agent.add_sensor('touch', 'touch_1', resolution = 64)
# my_agent.add_sensor('infra-red', 'IR_1', number = 5, fov = 90)




# other_agent = agent.Agent('forward', name='other', controller_type='random', position = [200, 200, 0])
# agents.append(other_agent)

from flatland.game_engine import Engine


game = Engine(playground=pg, agents=agents, time_limit=1000, replay=True)


import cv2
import time
import numpy
t1 = time.time()

while game.game_on:

    actions = {}
    for agent in game.agents:
        actions[agent.name] = agent.controller.generate_actions()

    game.step(actions)
    game.update_observations()


    for agent in game.agents:

        # observations = agent.observations
        # print(observations)

        for sensor_ in agent.sensors:

            observation = sensor_.sensor_value
            sensor_name = sensor_.name

            # print(observation.shape, sensor.shape())

            if isinstance(sensor, SemanticSensor) :

                print('---')
                for ang, obs in observation.items():

                    for o in obs:

                        print(ang, o.distance, o.entity)

            elif isinstance(sensor, TopdownSensor):
                cv2.imshow(sensor_name + '__', observation)
                cv2.waitKey(1)


            else:

                im = numpy.expand_dims(observation, 0)
                im = cv2.resize(im, (512, 50), interpolation=cv2.INTER_NEAREST)
                #im = observation
                cv2.imshow(sensor_name+'__', im)
                cv2.waitKey(1)

        if agent.reward != 0: print(agent.name, agent.reward)



    # for entity in game.playground.entities:
    #     if entity.velocity[0] != 0:
    #         print(entity.position)
    #         print(entity.velocity)
    #
    img = game.generate_topdown_image()
    cv2.imshow('test', img)
    cv2.waitKey(30)

    game.display_full_scene()


print(1000 / (time.time() - t1))
# game.terminate()
