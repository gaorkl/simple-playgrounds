import time, math

################# Test scenes

import flatland.scenes as scenes
test_scene = scenes.SceneGenerator.create( 'basic' )

scene_params = {'walls_depth': 50}
test_scene = scenes.SceneGenerator.create( 'basic' , scene_params)

test_scene = scenes.SceneGenerator.create( 'rooms_2' , scene_params)


################# Test playground

import flatland.playgrounds as playgrounds
pg = playgrounds.PlaygroundGenerator.create( 'basic_empty' )
pg.display_playground()

scene_params = {'walls_depth': 50}
pg_params = { 'scene': scene_params}
pg = playgrounds.PlaygroundGenerator.create( 'basic_empty', pg_params )
pg.display_playground()

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

pg = playgrounds.PlaygroundGenerator.create( 'basic_empty', pg_params )
pg.display_playground()

pg = playgrounds.PlaygroundGenerator.create( 'basic_field', pg_params )


scene_params = {'walls_depth': 20}
pg_params = { 'scene': scene_params }
pg = playgrounds.PlaygroundGenerator.create( 'rooms_2_empty', pg_params )
pg.display_playground()

############## Agent
import flatland.agents.agent as agent

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
ag = agent.BasicAgent(agent_parameters, controller = 'human')


############### Create game with playground and parameters
from . import game_engine

game_parameters = {
    'rules':{
        'game_mode' : 'time',
        'horizon' : 1000
    },
    'engine' : {
        'speed_ratio': 1,
        'aspect_ratio': 1,
    },
    'display': {
        'playground' : True,
        'internals' : False,
        'sensors' : False
    }
}

game = game_engine.Engine( playground = pg, agents = [ag], params = game_parameters)




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
