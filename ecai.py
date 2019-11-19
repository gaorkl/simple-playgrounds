import pygame
import numpy as np
import cv2

###########################################
# BUILDING A PLAYGROUND
###########################################
import flatland.playgrounds.playground as playground

from stable_baselines.results_plotter import load_results, ts2xy
from stable_baselines import results_plotter
import numpy as np
import matplotlib.pyplot as plt
from stable_baselines.bench import Monitor


log_dir = "log/"



#################################################
##### BUILDING AN AGENT
#################################################

from flatland.agents import agent
from flatland.default_parameters.agents import *

agent_params = {
    'frame': {
        'type': 'forward',
        'params': {
            'base_radius': 10,
                }
    },
    'controller': {
        'type': 'keyboard'
    },
    'sensors': {
        'rgb_1': {**rgb_default, **{'bodyAnchor': 'base', 'fovResolution': 64, 'fovRange': 300} },
        #'touch_1' : touch_default,
    },

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
    'replay_until_time_limit': False,
    'time_limit': 500
}



pg_params = {
    'playground_type': 'no_touching',
}

pg = playground.PlaygroundGenerator.create( pg_params )

game = Engine(playground=pg, agents=[my_agent], rules=rules, engine_parameters=engine_parameters )

from  flatland.gym_wrapper import CustomEnv
from stable_baselines import TRPO
from stable_baselines.common.vec_env import DummyVecEnv


env = CustomEnv(game, my_agent)
env = Monitor(env, log_dir, allow_early_resets=True)

# Instantiate the agent
model = TRPO('MlpPolicy', env, verbose=1)
# Train the agent

time_steps = 1e5

for i in range(10):
    model.learn(total_timesteps=int(time_steps/5))
    model.save("trpo_test")

    #model.load("trpo_test")
    # Enjoy trained agent
    obs = env.reset()
    for i in range(1000):
        action, _states = model.predict(obs)
        obs, rewards, done, info = env.step(action)
        if done: env.reset()
        env.render()

results_plotter.plot_results([log_dir], time_steps, results_plotter.X_TIMESTEPS, "DDPG LunarLander")
plt.show()