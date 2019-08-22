import math
import pygame

from pygame.locals import *

from .sensors import sensor
from .controllers import controller
from .frames import frame
from ..default_parameters.agents import *

class Agent():

    def __init__(self, agent_params):
        super(Agent, self).__init__()

        agent_params = {**agent_params, **metabolism_default }

        self.health = agent_params.get('health')
        self.base_metabolism = agent_params.get('base_metabolism')
        self.action_metabolism = agent_params.get('action_metabolism')

        # Create Frame
        frame_params = agent_params.get('frame', {})
        self.frame = frame.FrameGenerator.create(frame_params)
        self.available_actions = self.frame.get_available_actions()

        # Add all necessary sensors
        self.sensors = {}
        for sensor_name, sensor_params in agent_params.get('sensors', {}).items():
            sensor_params['name'] = sensor_name
            self.add_sensor(sensor_params)

        # Select Controller
        controller_params = agent_params.get('controller', {})
        self.controller = controller.ControllerGenerator.create(controller_params)

        self.controller.set_available_actions(self.available_actions)

        if self.controller.require_key_mapping:
            default_key_mapping = self.frame.get_default_key_mapping()
            self.controller.assign_key_mapping(default_key_mapping)


        # Internals
        self.reward = 0
        self.is_activating = False
        self.is_eating = False
        self.is_grasping = False
        self.grasped = []
        self.is_holding = False

        self.observations = {}
        self.action_commands = {}

        # Default starting position
        self.starting_position = agent_params.get('starting_position', None)


    def add_sensor(self, sensor_param):

        sensor_param['minRange'] = self.frame.base_radius   # To avoid errors while logpolar converting
        new_sensor = sensor.SensorGenerator.create(self.frame.anatomy, sensor_param)
        self.sensors[new_sensor.name] = new_sensor

    def compute_sensors(self, img):

        for sens in self.sensors:
            self.sensors[sens].update_sensor(img)

            self.observations[sens] = self.sensors[sens].observation

    def pre_step(self):

        self.reward = 0
        self.action_commands = {}

    def get_actions(self):

        self.action_commands = self.controller.get_actions()

    def apply_action(self):

        self.is_activating = bool(self.action_commands.get('activate', 0))
        self.is_eating = bool(self.action_commands.get('eat', 0))
        self.is_grasping = bool(self.action_commands.get('grasp', 0))

        if self.is_holding and not self.is_grasping:
            self.is_holding = False

        # Compute energy and reward
        if self.is_eating: self.reward -= self.action_metabolism
        if self.is_activating: self.reward -= self.action_metabolism
        if self.is_holding: self.reward -= self.action_metabolism

        self.frame.apply_actions(self.action_commands)

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
