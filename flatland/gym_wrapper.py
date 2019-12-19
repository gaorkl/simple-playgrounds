import gym
from gym import spaces
import numpy as np
import cv2

import pygame
clock = pygame.time.Clock()

class CustomEnv(gym.Env):
  """Custom Environment that follows gym interface"""
  metadata = {'render.modes': ['human']}

  def __init__(self, game, agent):
    super(CustomEnv, self).__init__()
    # Define action and observation space
    # They must be gym.spaces objects
    # Example when using discrete actions:

    self.game = game
    self.agent = agent

    self.action_space = spaces.Box(low=-1, high=1, shape=(2,) )  # up

    # Example for using image as input:
    self.observation_space = spaces.Box(low=0, high=255, shape=(1,64,3), dtype=np.uint8) #rgb

  def step(self, action):

      agent_actions = {
          'activate': 0,
          'eat':0,
          'grasp':0,
          'longitudinal_velocity': (action[0] + 1) / 2.0,
          'angular_velocity':action[1],
          'head_velocity': 0
      }

      self.agent.get_actions(agent_actions)
      self.game.set_actions()


      self.game.step()

      self.game.update_observations()

      observations = self.agent.observations
      rgb = np.asarray(observations['rgb_1'])
      rgb = np.expand_dims(rgb, 0)

      obs = (rgb*255).astype(int)

      reward = self.agent.spot_reward

      if self.game.playground.has_reached_termination:
          done = True

      elif not self.game.game_on:
          done = True
      else: done = False

      return (obs, reward, done, {})


  def reset(self):

    self.game.game_reset()
    self.game.time = 0
    self.game.game_on = True

    state, rewards, done, _ = self.step([0,0,0])
    return state

  def render(self, mode='human'):
    self.game.display_full_scene()
    img = self.game.playground.generate_playground_image()
    cv2.imshow('img', img)
    cv2.waitKey(1)

    clock.tick(100)
