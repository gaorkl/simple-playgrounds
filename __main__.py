import pygame
import numpy as np
import cv2

###########################################
# BUILDING A PLAYGROUND
###########################################
import flatland.playgrounds.playground as playground
from flatland.default_parameters.entities import *

### Basic entities
basic_1 = basic_default.copy()
basic_1['position'] = [100, 50, math.pi/2]
basic_1['physical_shape'] = 'rectangle'
basic_1['shape_rectangle'] = [10,30]

basic_2 = basic_default.copy()
basic_2['position'] = [100, 100, math.pi/2]
basic_2['physical_shape'] = 'hexagon'
basic_2['radius'] = 20
basic_2['texture'] = {
    'type': 'uniform_grained',
    'min': [150, 0, 50],
    'max': [200, 0, 100],
    'size_grains': 4
}

basic_3 = basic_default.copy()
basic_3['position'] = [100, 150, 0]
basic_3['physical_shape'] = 'pentagon'
basic_3['radius'] = 20
basic_3['movable'] = False

basic_3['texture'] = {
    'type': 'polar_stripes',
    'color_1': [0, 0, 150],
    'color_2': [0, 0, 250],
    'n_stripes' : 5
}

###### Absorbable

absorbable_1 = absorbable_default.copy()
absorbable_1['position'] = [100, 200, 0.2]

absorbable_2 = absorbable_default.copy()
absorbable_2['position'] = [100, 250,0.5]


### Edible

edible_1 = edible_default.copy()
edible_1['position'] = [100, 300, 0.2]
edible_1['physical_shape'] = 'rectangle'
edible_1['mass'] = 100
edible_1['shape_rectangle'] = [20, 30]
edible_1['movable'] = True
edible_1['graspable'] = True


### Dispenser
dispenser_1 = dispenser_default.copy()
dispenser_1['position'] = [100, 350,0]
dispenser_1['area'] = [[200, 325],[250, 375]]
dispenser_1['limit'] = 7

### Yielder
yielder_1 = yielder_default.copy()
yielder_1['area'] = [[100, 400],[200, 500]]



### Zone
end_zone = end_zone_default.copy()
end_zone['position'] = [250, 50, 0]
end_zone['physical_shape'] = 'rectangle'
end_zone['shape_rectangle'] = [50,50]

healing_zone = healing_zone_default.copy()
healing_zone['position'] = [250, 100, 0]
healing_zone['visible'] = True

damaging_zone = damaging_zone_default.copy()
damaging_zone['position'] = [250, 150, 0]

##### Button door
button_door_1 = button_door_openclose_default.copy()
button_door_1['position'] = [250, 200, 0]
button_door_1['door']['position'] = [250, 250, math.pi/2]

##### Button door
button_door_2 = button_door_opentimer_default.copy()
button_door_2['position'] = [250, 300, 0]
button_door_2['door']['position'] = [250, 350, math.pi/2]



pg_params = {
    'scene': {
        'shape': [600, 400]
    },
    'entities': [basic_1, basic_2, basic_3, absorbable_1, absorbable_2, edible_1, dispenser_1, yielder_1,
                 end_zone, healing_zone, damaging_zone,
                 button_door_1, button_door_2]
}

pg = playground.PlaygroundGenerator.create('basic', pg_params )

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
        'rgb_1': {**rgb_default, **{'bodyAnchor': 'head', 'fovResolution': 512} },
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

# import time
# t1 = time.time()

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

    # print(game.time, my_agent.health)

    clock.tick(30)

# print( 1000/(time.time() - t1) )
