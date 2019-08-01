import time, math
import pygame




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
    'shink_when_eaten': 0.9,
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
    'base_metabolism': 0.01,
    'action_metabolism': 1,
    'head_range': math.pi/2,
    'head_speed': 0.05
    #TODO: Add base / moving / eating metabolism
}
ag = forward_head.ForwardHeadAgent(agent_parameters)


############### Brain Controller
#import flatland.controllers.human as human_controller
import flatland.controllers.random as random_controller

available_actions = ag.getAvailableActions()
kb_control = random_controller.Random(available_actions)


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
        'internals' : False,
        'sensors' : False,
    }
}

dict_agents = {
    'test_agent': {
        'agent': ag,
        'controller': kb_control
    }
}

game = Engine( playground = pg_rooms_2_edible, agents = dict_agents, params = game_parameters )


clock = pygame.time.Clock()


while game.game_on:

    game.get_observations()
    game.set_actions()
    game.step()

    game.display()

    clock.tick(60)






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
