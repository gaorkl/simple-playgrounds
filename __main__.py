import pygame
import numpy as np
import cv2

import flatland.playgrounds as playgrounds
from flatland.default_parameters.entities import *


new_entity = basic_default.copy()
new_entity['position'] = [50, 50, 0.2]
new_entity['physical_shape'] = 'rectangle'
new_entity['shape_rectangle'] = [30, 60]

pg_params = {
    'scene': {
        'shape': [600, 200]
    },
    'entities': [new_entity]
}


pg = playgrounds.PlaygroundGenerator.create('rooms_2_edible', pg_params )
#img = pg.generate_playground_image()
#display(img)

### Basic entities
basic_1 = basic_default.copy()
basic_1['position'] = [80, 80, 0.2]
basic_1['physical_shape'] = 'triangle'
basic_1['radius'] = 20


basic_1['texture'] = {
    'type': 'uniform_grained',
    'min': [150, 0, 50],
    'max': [200, 0, 100],
    'size_grains': 8
}



basic_2 = basic_default.copy()
basic_2['position'] = [80, 120, 0]
basic_2['physical_shape'] = 'pentagon'
basic_2['radius'] = 30
basic_2['movable'] = False

basic_2['texture'] = {
    'type': 'polar_stripes',
    'color_1': [0, 0, 150],
    'color_2': [250, 0, 100],
    'n_stripes' : 10
}



### Edibles

edible_1 = edible_default.copy()
edible_1['position'] = [200, 50, 0.2]
edible_1['physical_shape'] = 'pentagon'
edible_1['mass'] = 100
edible_1['radius'] = 20
edible_1['movable'] = False

### Absorbables

absorbable_1 = absorbable_default.copy()
absorbable_1['position'] = [350, 200, 0.2]

absorbable_2 = absorbable_default.copy()
absorbable_2['position'] = [350, 220,0.5]

### Dispenser

dispenser_1 = dispenser_default.copy()
dispenser_1['position'] = [350, 50,0]
dispenser_1['area'] = [[360, 100],[380, 120]]

### Yielder

yielder_1 = yielder_default.copy()
yielder_1['area'] = [[100, 400],[200, 600]]

### Graspable
grasp_1 = graspable_default.copy()
grasp_1['position'] = [150, 200 ,0]

### Door
door_opener = door_opener_default.copy()
door_opener['door']['position'] = [200, 300, math.pi/2]
door_opener['position'] = [50, 300, 0]

pg_params = {
    'scene': {
        'shape': [600, 400]
    },
    'entities': [basic_1, basic_2, edible_1, absorbable_1, absorbable_2, dispenser_1, yielder_1, grasp_1, door_opener]
}

pg = playgrounds.PlaygroundGenerator.create('rooms_2_edible', pg_params )
#img = pg.generate_playground_image()
#display(img)

############## Agent
import flatland.agents.mechanics.forward_head as forward_head

agent_parameters = {
    'starting_position' : {
        'type': 'fixed',
        'position' : [200, 200, 0]
    }
}

ag = forward_head.ForwardHeadAgent(agent_parameters)


############### Brain Controller
import flatland.agents.controllers.human as human_controller

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
        'mechanics' : True,
    }
}


dict_agents = {
    'test_agent': {
        'agent': ag,
        'controller': kb_control
    }
}

game = Engine( playground = pg, agents = dict_agents, game_parameters = game_parameters )


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
            cv2.waitKey(1)

    game.display_full_scene()



    clock.tick(20)


# TODO: compare dynamics of basic object and actionable object + action radius (effects of having 2 bodies)



#rat = agent.Rat()
#print(rat) # Should print agent details

#control = controller.Keyboard(rat)
#print(control)

#pg = playground( scene = basic_scene, mechanics = [rat] )

#obs = None
#act = None

#for t in range(1000):

#    obs = pg.step( act )

#    controller.get_action( obs )

    # In case of RL:
    # controller.update()
