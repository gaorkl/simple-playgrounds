import cv2
import time
import json
import pandas as pd

from flatland.game_engine import Engine
from flatland.tests.test_basics.entities_pg import *
from flatland.agents import agent

#Warning : not up to date


Agent = agent.Agent

def run(nbAgents = 10, mapSize = 200, steps = 100, depth = False, fullBlind = False, display = False, map = "basic_01"):


    engine_parameters = {
        'inner_simulation_steps': 5,
        'scale_factor': 1,

        'display': {
            'playground' : False,
            'body_parts' : True,
        }
    }

    rules = {
        'replay_until_time_limit': True,
        'time_limit': steps
    }


    pg = PlaygroundGenerator.create(map, room_shape = [mapSize, mapSize])

    agents = []

    #Generating agents
    for i in range(nbAgents):

        my_agent = Agent('forward', controller_type='random')

        #Full Blind == no image calculation at all
        if fullBlind:
            my_agent.fullBlind = True
        else:
            my_agent.fullBlind = False
            #Depth == the image is used to compute the depth sensor
            if depth:
                my_agent.add_sensor('depth', 'depth_1', fov_resolution = 128)

        my_agent.starting_position = {
            'type': 'rectangle',
            'x_range': [20, 80],
            'y_range': [20, 80],
            'angle_range': [0, 3.14 * 2],
        }

        agents.append(my_agent)

    game = Engine(playground=pg, agents=agents, rules=rules, engine_parameters=engine_parameters)

    t1 = time.time()
    while game.game_on:

        actions = {}
        for agent in game.agents:
            actions[agent.name] = agent.get_controller_actions()

        #Updating game steps and observations
        game.multiple_steps(actions, 1)
        game.update_observations()

        #Visualisation

        if display:
            img = game.generate_playground_image()
            cv2.imshow('Flatland', img)
            cv2.waitKey(1)

    game.terminate()
    t2 = time.time()

    delta = t2 - t1
    #Note : print(agent) ---> la variable globale agent devient une instance de agent, fait que ce code est pas réutilisable dirctement
    #sans le tricks de renommer
    return delta

def add_row(df, row):
    df.loc[-1] = row
    df.index = df.index + 1
    return df.sort_index()


nbAgents = [10]
mapSize = [200]
depth = [True]
fullBlind = [True]


# nbAgents = [1,10,30,50]
# mapSize = [200,400,600,800]
# depth = [False,True]
# fullBlind = [True]

results = pd.DataFrame(columns = ["nbAgents","mapSize","depth","fullBlind","perf"])

# for nb in nbAgents:
#     for size in mapSize:
#         for d in depth:
#             print(nb,size,d)
#             perf = run(nbAgents = nb, mapSize = size, depth = d)
#             print(perf)
#             add_row(results,[nb,size,d,perf])
#             print("*******")

# for nb in nbAgents:
#     for size in mapSize:
#         for d in depth:
#             for f in fullBlind:
#                 print(nb,size,d,f)
#                 perf = run(nbAgents = nb, mapSize = size, depth =d, fullBlind = f)
#                 print(perf)
#                 add_row(results,[nb,size,d,f,perf])
#                 print("*******")

import test_basics.test
perf = run(nbAgents = 2, map = "moving_01", mapSize = 100, display = True, steps = 500, fullBlind = True)


#results.to_csv('perftest-results.csv', index=False)
