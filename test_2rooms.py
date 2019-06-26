import playground
import math
import pygame
from pygame.locals import *

scene_parameters = {
    'scene_type': '2-rooms',
    'shape': (200, 400),
    'walls_depth': 10,
    'walls_texture':
        {
        'texture_type': 'color',
        'color': (124, 110, 1)
        }
    }


game_parameters = {
    'horizon' : 1000,
    'normalize_measurements': False,
    'normalize_states': False,
    'normalize_rewards': False
    }

engine_parameters = {
    'display_playground': True,
    'display_agent_measures': True,
    'speed_ratio': 1,
    'aspect_ratio': 1,
}

# speeds in units/timestep
# rotation speed in rad/timestep
agent_parameters = {
    'color': (0, 200, 0),
    'speed': 1.0,
    'rotation_speed': (2*math.pi)/100 ,
    'position':  [50, 50, math.pi/2.0],
    'health': 1000,
    'base_metabolism': 0.01,
    'action_metabolism': 1
    #TODO: Add base / moving / eating metabolism
}

pg = playground.Playground( scene_parameters = scene_parameters,
                            game_parameters = game_parameters,
                            engine_parameters = engine_parameters,
                            agent_parameters = agent_parameters)


## Edible objects

new_object = {
    'physical_shape': 'circle',
    'radius': 20,
    'position':  [70, 300, 0],
    'default_color':(100, 50, 100),
    'movable': False,

    'entity_type':'actionable',
    'actionable_type': 'edible',
    'action_radius':10,
    # TODO: replace shrink
    'shink_when_eaten': 0.9,
    'mass': 10,
    'initial_reward' : 30
}
pg.addEntity( new_object )

#

# Pellet dispenser
#
# pellet = {
#     'physical_shape': 'circle',
#     'radius': 5,
#     'default_color':(0, 250, 0),
#     'absorbable': True,
#     'movable' : True,
#     'mass' : 5,
#     'reward' : 5
# }
#
# new_object = {
#     'physical_shape': 'circle',
#     'radius': 20,
#     'position':  [150, 150, 0],
#     'default_color':(0, 250, 0),
#     'mass': 10,
#     'movable': False,
#
#     'entity_type': 'actionable',
#     'actionable_type': 'dispenser',
#     'action_radius':10,
#     'object': pellet,
#     'limit':5,
#     'area_shape': 'rectangle',
#     'area': ( (50, 50), (100, 100) )
# }
#
# pg.addEntity( new_object )




# Change colors, distractor

# new_object = {
#     'physical_shape': 'circle',
#     'radius': 20,
#     'position':  [150, 150, 0],
#     'default_color':(124, 0, 10),
#     'movable': False,
#
#     'entity_type':'actionable',
#     'actionable_type': 'distractor',
#     'action_radius':10,
#     'mass': 10
# }
#
# pg.addEntity( new_object )

#
# Open door

door = {
    'physical_shape': 'box',
    'size_box': (5, 50 ),
    'position':  [165, 200, math.pi/2],
    'default_color':(0, 150, 200),
    'movable': False
}

new_object = {
    'physical_shape': 'circle',
    'radius': 10,
    'position':  [50, 200, 0],
    'default_color':(0, 250, 0),
    'mass': 10,
    'movable': False,

    'entity_type':'actionable',
    'actionable_type': 'door',
    'door': door,
    'action_radius':10,
    'time_open': 400
}

pg.addEntity( new_object )


#
#

# pellet = {
#     'physical_shape': 'circle',
#     'radius': 5,
#     'default_color':(0, 250, 0),
#     'absorbable': True,
#     'movable' : True,
#     'mass' : 5,
#     'reward' : 5
# }
#
# #
# new_object = {
#     'entity_type':'yielder',
#
#     'object': pellet,
#     'area_shape': 'rectangle',
#     'area': ((150, 150), (200, 200)),
#     'probability': 1.0/60,
#     'limit': 5
# }
#
# pg.addEntity(new_object)



clock = pygame.time.Clock()
actions = {}

ready_to_press_a = True
ready_to_press_e = True


while True:
    #actions['longitudinal_velocity'] = 1.0

    #print(ready_to_press_a)

    actions['activate'] = 0.0
    actions['eat'] = 0.0


    for event in pygame.event.get():



        if event.type == KEYDOWN:
            if event.key == K_z:
                actions['longitudinal_velocity'] = 1.0

            if event.key == K_a:
                if ready_to_press_a:
                    actions['activate'] = 1.0
                    ready_to_press_a = False

            if event.key == K_e:
                if ready_to_press_e:
                    actions['eat'] = 1.0
                    ready_to_press_e = False


            if event.key == K_LEFT:
                actions['angular_velocity'] = 1.0

            if event.key == K_RIGHT:
                actions['angular_velocity'] = -1.0


        if event.type == KEYUP:
            if event.key == K_z:
                actions['longitudinal_velocity'] = 0.0

            if event.key == K_LEFT:
                actions['angular_velocity'] = 0.0

            if event.key == K_RIGHT:
                actions['angular_velocity'] = 0.0

            if event.key == K_a:
                ready_to_press_a = True

            if event.key == K_e:
                ready_to_press_e = True

    #print(actions)
    pg.step(actions)
    pg.draw()

    clock.tick(60)