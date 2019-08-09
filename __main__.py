import time, math
import pygame
import matplotlib.pyplot as plt
import numpy as np
import cv2


################# Test scenes

import flatland.scenes as scenes
test_scene = scenes.SceneGenerator.create( 'basic' )

scene_params = {'walls_depth': 50}
test_scene = scenes.SceneGenerator.create( 'basic' , scene_params)


test_scene = scenes.SceneGenerator.create( 'rooms_2' , scene_params)


################# Test playground

import flatland.playgrounds as playgrounds
pg = playgrounds.PlaygroundGenerator.create( 'basic_empty' )

scene_params = {'walls_depth': 50}
pg_params = { 'scene': scene_params}
pg = playgrounds.PlaygroundGenerator.create( 'basic_empty', pg_params )

scene_params = {'walls_depth': 50}
edible = {
    'physical_shape': 'circle',
    'radius': 15,
    'position':  [200, 200, 0],
    'default_color':(0, 250, 100),
    'movable': True,

    'entity_type':'actionable',
    'actionable_type': 'edible',
    'action_radius':10,
    'shrink_when_eaten': 0.9,
    'mass': 10,
    'initial_reward' : 30
}

pg_params = { 'scene': scene_params,
              'entities': [edible]}

pg_basic_empty = playgrounds.PlaygroundGenerator.create( 'basic_empty', pg_params )
pg_basic_field = playgrounds.PlaygroundGenerator.create( 'basic_field', pg_params )


scene_params = {'walls_depth': 20}
pg_params = { 'scene': scene_params }
pg_rooms_2_edible = playgrounds.PlaygroundGenerator.create( 'rooms_2_edible', pg_params )

############## Agent
import flatland.agents.forward_head as forward_head

agent_parameters = {
    'color': (0, 200, 0),
    'speed': 1.0,
    'rotation_speed': (2*math.pi)/50 ,
    'position':  [50, 50, math.pi/2.0],
    'health': 1000,
    'base_metabolism': 0.00,
    'action_metabolism': 0.00,
    'head_range': math.pi/2,
    'head_speed': 0.05,
    'radius': 20,
    'head_radius' : 10,

    'sensors':

            [
                {
                    'name': 'rgb_1',
                    'type': 'rgb',
                    'fovResolution': 128,
                    'fovRange': 100,
                    'fovAngle': math.pi,
                    'bodyAnchor': "head",
                    'd_r': 0,
                    'd_theta': 0,
                    'd_relativeOrientation': 0
                },

                {
                    'name': 'touch_1',
                    'type': 'touch',
                    'fovResolution': 128,
                    'fovRange': 25,
                    'fovAngle': 2*math.pi,
                    'bodyAnchor': "base",
                    'd_r': 0,
                    'd_theta': 0,
                    'd_relativeOrientation': 0
                }
            ]


    #TODO: Add base / moving / eating metabolism
}


ag_1 = forward_head.ForwardHeadAgent(agent_parameters)

agent_parameters['position'][0] = 100
ag_2 = forward_head.ForwardHeadAgent(agent_parameters)


############### Brain Controller
import flatland.controllers.human as human_controller
import flatland.controllers.random as random_controller

available_actions = ag_1.getAvailableActions()
rd_control = random_controller.Random(available_actions)

kb_mapping = ag_2.getStandardKeyMapping()
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
        'agent': ag_2,
        'controller': kb_control

    }
}

game = Engine( playground = pg_rooms_2_edible, agents = dict_agents, params = game_parameters )


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
