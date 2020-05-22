from flatland.playgrounds.empty import  ConnectedRooms2D, SingleRoom, LinearRooms
from flatland.agents import agent
from flatland.utils.position_utils import PositionAreaSampler

from flatland.tests.test_basics.test_advanced_playgrounds import Rooms_Doors

# pg = SingleRoom((200, 300), wall_type='colorful')
pg = Rooms_Doors()
# pg = ConnectedRooms2D((800, 800), (3, 3) , doorstep_type='random', wall_type='colorful')


agents = []

initial_position = PositionAreaSampler(area_shape='circle', center=[50, 50], radius=40)
my_agent = agent.Agent('forward', name = 'mercotte',
                       controller_type = 'keyboard',
                       frame = { 'base': {'radius' : 10}},
                       position=initial_position)

my_agent.add_sensor('rgb', 'rgb_1', resolution = 128, fov = 180, range=100)
agents.append(my_agent)


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