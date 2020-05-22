import time
import json
import pandas as pd
import cv2

from flatland.game_engine import Engine
from flatland.tests.test_basics.entities_pg import *
from flatland.agents import agent


Agent = agent.Agent

def run(nbAgents = 1, mapSize = 200, steps = 100, display = False, map = "basic_01"):


    engine_parameters = {
        'inner_simulation_steps': 5,
        'scale_factor': 1,

        'display': {
            'playground' : False,
            'frames' : True,
        }
    }

    rules = {
        'replay_until_time_limit': True,
        'time_limit': steps
    }


    pg = PlaygroundGenerator.create(map, room_shape = [mapSize, mapSize])

    agents = []

    initial_position = PositionAreaSampler(area_shape='circle', center=[120, 120], radius=30)

    #Generating agents
    for i in range(nbAgents):

        my_agent = Agent('forward', controller_type='random', position =initial_position)
        my_agent.add_sensor('lidar', 'lidar_1', someArgument = "argument")

        # my_agent.starting_position = {
        #     'type': 'rectangle',
        #     'x_range': [20, 80],
        #     'y_range': [20, 80],
        #     'angle_range': [0, 3.14 * 2],
        # }

        agents.append(my_agent)

    game = Engine(playground=pg, agents=agents, rules=rules, engine_parameters=engine_parameters)

    t1 = time.time()
    while game.game_on:

        actions = {}
        for agent in game.agents:
            actions[agent.name] = agent.get_controller_actions()

        #Updating game steps and observations
        game.step(actions)
        game.update_observations()

        #Visualisation

        if display:
            img = game.generate_playground_image()
            cv2.imshow('Flatland', img)
            cv2.waitKey(15) #15

    game.terminate()

 # code à lancer pour tester le capteur
perf = run(nbAgents = 1, map = "activable_01", mapSize = 300, display = True, steps = 100)
