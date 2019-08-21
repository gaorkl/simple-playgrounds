import math
import pymunk, pygame

from pygame.locals import *

from .sensors import sensor
from .controllers import controller
from .physical_bodies import physical_body

class Agent():

    def __init__(self, agent_params):
        super(Agent, self).__init__()

        self.health = agent_params.get('health')
        self.base_metabolism = agent_params.get('base_metabolism')
        self.action_metabolism = agent_params.get('action_metabolism')

        self.reward = 0

        self.is_activating = False
        self.grasped = []
        self.is_holding = False

        self.sensors = []
        for sensor_param in agent_params.get('sensors', []):
            self.add_sensor(sensor_param)

        self.observations = {}


    def add_sensor(self, sensor_param):

        sensor_param['minRange'] = self.base_radius   # To avoid errors while logpolar converting
        new_sensor = sensor.SensorGenerator.create(self.anatomy, sensor_param)
        self.sensors[new_sensor.name] = new_sensor

    def compute_sensors(self, img):

        for sens in self.sensors:
            self.sensors[sens].update_sensor(img)

            self.observations[sens] = self.sensors[sens].observation

    def pre_step(self):

        self.reward = 0
        self.actions = []


    def draw(self,  surface):

        """
        Draw the agent on the environment screen
        """
        # Body

        mask_rotated = pygame.transform.rotate(self.mask, self.anatomy['base'].body.angle * 180 / math.pi)
        mask_rect = mask_rotated.get_rect()
        mask_rect.center = self.anatomy['base'].body.position[1], self.anatomy['base'].body.position[0]

        # Blit the masked texture on the screen
        surface.blit(mask_rotated, mask_rect, None)


    def apply_action(self, actions):

        self.is_activating = bool(actions.get('activate', 0))
        self.is_eating = bool(actions.get('eat', 0))

        self.is_grasping = bool(actions.get('grasp', 0))


        if self.is_holding and not self.is_grasping:
            self.is_holding = False

        # Compute energy and reward
        if self.is_eating: self.reward -= self.action_metabolism
        if self.is_activating: self.reward -= self.action_metabolism

        self.reward -= self.base_metabolism * (abs(longitudinal_velocity) + abs(angular_velocity))
        self.health += self.reward

    def getStandardKeyMapping(self):
        mapping = {
            K_g: ['press_hold', 'grasp', 1],
            K_a: ['press_once', 'activate', 1],
            K_e: ['press_once', 'eat', 1]

        }

        return mapping

    def getAvailableActions(self):

        actions = {
            'grasp': [0, 1, 'discrete'],
            'activate': [0, 1, 'discrete'],
            'eat': [0, 1, 'discrete'],
        }

        return actions