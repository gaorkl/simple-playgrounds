import pygame
import numpy as np
import cv2

###########################################
# BUILDING A PLAYGROUND
###########################################
import flatland.playgrounds.playground as playground

pg_params = {
    'playground_type': 'basic_endzone_contact_fireball',
    'scene': {
        'scene_shape': [100, 500]
    },
}

pg = playground.PlaygroundGenerator.create( pg_params )

#################################################
##### BUILDING AN AGENT
#################################################

import flatland.agents.agent as agent
from flatland.default_parameters.agents import *

agent_params = {
    'frame' : {
        'type': 'forward_head',
        'params' : {
            'base_radius': 15,
                }
    },
    'controller' :{
        'type': 'keyboard'
    },
    'sensors':{
        'rgb_1': {**rgb_default, **{'bodyAnchor': 'head', 'fovResolution': 128, 'fovRange': 1000} },
        'rgb_2': {**rgb_default, **{'bodyAnchor': 'head', 'fovResolution': 64, 'fovRange': 250} },
        'rgb_3': {**rgb_default, **{'bodyAnchor': 'head', 'fovAngle': math.pi/2.0, 'fovRange': 250} },
        'touch_1' : touch_default,
    },
    'starting_position':{
        'type': 'fixed',
        'coordinates' : [50, 50, 0]
    }
}

my_agent = agent.Agent(agent_params)

####################################################
####### Create game with playground and parameters
####################################################

from flatland.game_engine import Engine

engine_parameters = {
    'inner_simulation_steps': 1,
    'scale_factor': 1,
    'display_mode': 'carthesian_view',

    'display': {
        'playground' : True,
        'frames' : True,
    }
}

rules = {
    'replay_until_time_limit': True,
    'time_limit' : 1000
}

game = Engine( playground = pg, agents = [my_agent], rules = rules, engine_parameters= engine_parameters )


clock = pygame.time.Clock()

import time
t1 = time.time()

while game.game_on:
    game.update_observations()
    game.set_actions()
    game.step()

    for agent in game.agents:

        observations = agent.observations

        for obs in observations:

            im = np.asarray( observations[obs])
            im = np.expand_dims(im, 0)
            im = cv2.resize( im, (512, 50), interpolation=cv2.INTER_NEAREST )
            cv2.imshow( obs, im )
            cv2.waitKey(1)

    game.display_full_scene()

    print(game.time, my_agent.health)

    clock.tick(30)

print( 1000/(time.time() - t1) )
