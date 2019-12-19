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
basic_1['position'] = [350, 350, math.pi/2]
basic_1['physical_shape'] = 'rectangle'
basic_1['shape_rectangle'] = [20,100]

basic_2 = basic_default.copy()
basic_2['position'] = [200, 100, math.pi/2]
basic_2['physical_shape'] = 'rectangle'
basic_2['shape_rectangle'] = [30,100]
basic_2['texture'] = {
    'type': 'random_tiles',
    'min': [150, 0, 50],
    'max': [200, 0, 100],
    'size_tiles': 4
}

basic_3 = basic_default.copy()
basic_3['position'] = [100, 150, 0]
basic_3['physical_shape'] = 'pentagon'
basic_3['radius'] = 20
basic_3['movable'] = False

basic_3['texture'] = {
    'type': 'centered_random_tiles',
    'radius' : 30,
    'min': [0, 50, 150],
    'max': [0, 100, 190],
    'size_tiles' : 5
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
edible_1['shape_rectangle'] = [50, 60]
edible_1['texture']['type']= 'random_tiles'
# edible_1['mass'] = 100
# edible_1['movable'] = True
# edible_1['graspable'] = True


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
end_zone['position'] = [500, 50, 0]
end_zone['physical_shape'] = 'rectangle'
end_zone['shape_rectangle'] = [50,50]

healing_zone = healing_zone_default.copy()
healing_zone['position'] = [500, 100, 0]
healing_zone['visible'] = True

damaging_zone = damaging_zone_default.copy()
damaging_zone['position'] = [500, 150, 0]

contact_endzone = contact_endzone_default.copy()
contact_endzone['position'] = [500, 550, 0]

##### Button door
button_door_1 = button_door_openclose_default.copy()
button_door_1['position'] = [600, 200, 0]
button_door_1['door']['position'] = [600, 250, math.pi/2]

##### Button door
button_door_2 = button_door_opentimer_default.copy()
button_door_2['position'] = [600, 350, 0]
button_door_2['door']['position'] = [600, 400, math.pi/2]
button_door_2['time_limit'] = 100


##### Lock_key door
lock_key_door = lock_key_door_default.copy()
lock_key_door['position'] = [600, 500, 0]
lock_key_door['door']['position'] = [600, 550, math.pi/2]
lock_key_door['key']['position'] = [600, 450, math.pi/2]

##### Moving object
moving_1 = basic_default.copy()
moving_1['position'] = [500, 500, math.pi/2]
moving_1['trajectory'] = {
    'trajectory_shape': 'line',
    'radius': 50,
    'center': [500, 500],
    'speed' : 100,

}

fireball_1 = fireball_default.copy()
fireball_1['position'] = [400, 500, math.pi/2]
fireball_1['trajectory'] = {
    'trajectory_shape': 'line',
    'radius': 60,
    'center': [400, 100],
    'angle' : math.pi/2,
    'speed' : 100,
}

fairy_1 = fairy_default.copy()
fairy_1['position'] = [400, 500, math.pi/2]
fairy_1['trajectory'] = {
    'trajectory_shape': 'pentagon',
    'radius': 30,
    'center': [400, 200],
    'speed' : 200,
}

pg_params = {
    'playground_type': 'basic_empty',
    'scene': {
        'scene_type': 'room',
        'scene_shape': [600, 800]
    },
    'entities': [basic_1, basic_2, basic_3, absorbable_1, absorbable_2, edible_1, yielder_1,
                 end_zone, healing_zone, damaging_zone, contact_endzone,
                 button_door_1, button_door_2, lock_key_door,
                 moving_1, fireball_1, fairy_1]
}

pg = playground.PlaygroundGenerator.create( pg_params )

#################################################
##### BUILDING AN AGENT
#################################################

import flatland.agents.agent as agent
from flatland.default_parameters.agents import *

agent_params = {
    'name': 'mercotte',
    'frame' : {
        'type': 'forward_head_arms',
        'params' : {
                }
    },
    'controller' :{
        'type': 'keyboard'
    },
    'sensors':{
        'rgb_1': {**rgb_default, **{'bodyAnchor': 'head', 'fovResolution': 356, 'fovRange': 1000} },
        'rgb_2': {**rgb_default, **{'bodyAnchor': 'head', 'fovResolution': 64, 'fovRange': 250} },
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
    'display_mode': 'carthesian_view',

    'display': {
        'playground' : True,
        'frames' : True,
    }
}

rules = {
    'replay_until_time_limit': True,
    'time_limit' : 10000
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
            im = cv2.resize( im, (im.shape[1] * 4, 50), interpolation=cv2.INTER_NEAREST )
            cv2.imshow( obs, im )
            cv2.waitKey(1)

    game.display_full_scene()

    print(game.time, my_agent.health)

    clock.tick(30)

print( 1000/(time.time() - t1) )
