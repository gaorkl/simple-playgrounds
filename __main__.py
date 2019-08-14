import time, math
import pygame
import matplotlib.pyplot as plt
import numpy as np
import cv2

import flatland.playgrounds as playgrounds
from flatland.common.default_entities_parameters import *


new_entity = basic_default.copy()
new_entity['position'] = [50, 50, 0.2]
new_entity['physical_shape'] = 'box'
new_entity['size_box'] = [30, 60]

pg_params = {
    'scene': {
        'shape': [600, 200]
    },
    'entities': [new_entity]
}


pg = playgrounds.PlaygroundGenerator.create('rooms_2_edible', pg_params )
#img = pg.generate_playground_image()
#display(img)

new_entity_1 = basic_default.copy()
new_entity_1['position'] = [50, 50, 0.0]
new_entity_1['physical_shape'] = 'triangle'
new_entity_1['radius'] = 20

new_entity_2 = edible_default.copy()
new_entity_2['position'] = [200, 50, 0.2]
new_entity_2['physical_shape'] = 'pentagon'
new_entity_2['radius'] = 20

pg_params = {
    'scene': {
        'shape': [600, 400]
    },
    'entities': [new_entity_1, new_entity_2]
}

pg = playgrounds.PlaygroundGenerator.create('rooms_2_edible', pg_params )
#img = pg.generate_playground_image()
#display(img)

############## Agent
import flatland.agents.forward_head as forward_head

agent_parameters = {
    'base_weight' : 5,
    'starting_position' : [200, 200, 0]
        # {
        #     'type': 'gaussian',
        #     'mean' : [100, 100, math.pi],
        #     'var' : [25, 25, 0.5]
        # }
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

    clock.tick(20)


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
