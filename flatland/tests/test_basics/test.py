from flatland.tests.test_basics.entities_pg import *
from flatland.tests.test_basics.advanced_pg import *
from flatland.agents import agent

# pg = Basic_01()
# pg = Contact_01()
# pg = Interactive_01()
# pg = Zones_01()
# pg = Proximity_01()
# pg = Trajectory_01()
#pg = Fields_01()

pg = Rooms_Doors()


# for entity in pg.entities:
#     print(entity)
#     print(entity.entity_type)
agents = []
#
# for i in range(10):
#     if i == 0:
#         my_agent = agent.Agent('forward', controller_type = 'keyboard')
#     else:
#         my_agent = agent.Agent('forward', controller_type='random')
#     my_agent.add_sensor('depth', 'depth_1', fov_resolution = 128)
#     #my_agent.add_sensor('touch', 'touch_1')
#     my_agent.starting_position = {
#                 'type': 'rectangle',
#                 'x_range': [80, 120],
#                 'y_range': [80, 120],
#                 'angle_range': [0, 3.14 * 2],
#             }
#
#     agents.append(my_agent)
#


initial_position = PositionAreaSampler(area_shape='circle', center=[50, 50], radius=40)
my_agent = agent.Agent('forward', name = 'mercotte',
                       controller_type = 'keyboard',
                       frame = { 'base': {'radius' : 10}},
                       position=initial_position)

#my_agent.add_sensor('depth', 'depth_1', resolution = 128)
#my_agent.add_sensor('rgb', 'rgb_1', resolution = 128, fov = 90)
# my_agent.add_sensor('rgb', 'rgb_2', resolution = 128)
# my_agent.add_sensor('touch', 'touch_1', resolution = 64)
# my_agent.add_sensor('infra-red', 'IR_1', number = 5, fov = 90)


agents.append(my_agent)

# other_agent = agent.Agent('forward', name='other', controller_type='random', position = [200, 200, 0])
# agents.append(other_agent)

from flatland.game_engine import Engine

engine_parameters = {
    'inner_simulation_steps': 5,
    'display': {
        'playground' : False,
        'frames' : True,
    }
}

rules = {
    'replay_until_time_limit': True,
    'time_limit': 10000
}

game = Engine(playground=pg, agents=agents, rules=rules, engine_parameters=engine_parameters )


import cv2
import time

t1 = time.time()


while game.game_on:

    actions = {}
    for agent in game.agents:
        actions[agent.name] = agent.get_controller_actions()

    game.step(actions)
    game.update_observations()


    for agent in game.agents:

        # observations = agent.observations
        # print(observations)

        for sensor_name in agent.sensors:

            observation = agent.sensors[sensor_name].sensor_value

            if 'IR' in  sensor_name:
                print(observation)

            else:

                im = cv2.resize(observation, (512, 50), interpolation=cv2.INTER_NEAREST)
                cv2.imshow(sensor_name, im)
                cv2.waitKey(1)

        if agent.reward != 0: print(agent.name, agent.reward)

    # for entity in game.playground.entities:
    #     if entity.velocity[0] != 0:
    #         print(entity.position)
    #         print(entity.velocity)

    img = game.generate_playground_image()
    cv2.imshow('test', img)
    cv2.waitKey(30)

print(1000 / (time.time() - t1))
game.terminate()