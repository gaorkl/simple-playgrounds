import time, math
import pygame
import matplotlib.pyplot as plt
import numpy as np
import cv2

from flatland.common.default_entities_parameters import *

################# Test scenes

import flatland.scenes as scenes
test_scene = scenes.SceneGenerator.create( 'basic' )

################# Test playground

import flatland.playgrounds as playgrounds

scene_params = {'walls_depth': 20}
pg_params = { 'scene': scene_params}
pg = playgrounds.PlaygroundGenerator.create( 'basic_empty', pg_params )

############## Agent
import flatland.agents.forward_head as forward_head

agent_parameters = {
    'base_weight' : 30,
    'starting_position' :
        {
            'type': 'gaussian',
            'mean' : [100, 100, math.pi],
            'var' : []
        }
}

ag = forward_head.ForwardHeadAgent(agent_parameters)

############### Brain Controller
import flatland.controllers.human as human_controller

kb_mapping = ag.getStandardKeyMapping()
kb_control = human_controller.Keyboard(kb_mapping)


############### Create game with playground and parameters
from flatland.game_engine import Engine

game_parameters = {
    'rules':{
        'game_mode' : 'time',
        'horizon' : 1000
    },
    'engine' : {
        'speed_ratio': 1,
        'aspect_ratio': 1,
        'frame_rate': 24
    },
    'display': {
        'playground' : True,
        'agents' : True,
    }
}

dict_agents = {
    # 'test_agent': {
    #     'agent': ag_1,
    #     'controller': rd_control
    # },
    'test_agent_2': {
        'agent': ag,
        'controller': kb_control

    }
}

game = Engine( playground = pg, agents = dict_agents, params = game_parameters )


clock = pygame.time.Clock()


while game.game_on:

    game.update_observations()
    game.set_actions()
    game.step()

    for agent in game.agents:

        observations = game.agents[agent]['agent'].observations

        for obs in observations:

            im = np.asarray( observations[obs])
            im = np.expand_dims(im, 0)
            im = cv2.resize( im, (512, 50), interpolation=cv2.INTER_NEAREST )
            cv2.imshow( obs, im )

    game.display_full_scene()

    clock.tick(120)


# TODO: compare dynamics of basic object and actionable object + action radius (effects of having 2 bodies)



#rat = agent.Rat()
#print(rat) # Should print agent details

#control = controller.Keyboard(rat)
#print(control)

#pg = playground( scene = basic_scene, agents = [rat] )

#obs = None
#act = None

#for t in range(1000):

#    obs = pg.step( act )

#    controller.get_action( obs )

    # In case of RL:
    # controller.update()
