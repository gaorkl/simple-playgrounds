import pygame
from pygame.locals import *
from flatland.agents.controllers.controller import ControllerGenerator, Controller
from flatland.utils.config import *

@ControllerGenerator.register_subclass('keyboard')
class Keyboard(Controller):

    def __init__(self):

        self.controller_type = 'keyboard'
        super().__init__()

        self.require_key_mapping = True
        self.press_state = {}
        self.key_mapping = {}

    def set_available_actions(self, available_actions):

        super().set_available_actions(available_actions)

        self.assign_key_mapping(available_actions)

    def assign_key_mapping(self, available_actions):

        for action in available_actions:

            if action.key in self.key_mapping:
                raise ValueError('Key assigned twice')

            self.key_mapping[action.key] = action
            if action.key_behavior == ActionTypes.PRESS_RELEASE:
                self.press_state[action.key_behavior] = True

    def reset_press_once_actions(self):

        for k, action in self.key_mapping.items():

            if action.key_behavior == ActionTypes.PRESS_RELEASE:
                self.actions[action.body_part][action.action] = 0

    def get_actions(self):

        self.reset_press_once_actions()

        for event in pygame.event.get():

            if event.type == KEYDOWN:

                if event.key in self.key_mapping:

                    action = self.key_mapping[event.key]

                    if action.key_behavior == ActionTypes.PRESS_RELEASE:
                        self.actions[action.body_part][action.action] = action.key_value
                        self.press_state[event.key] = False

                    elif action.key_behavior == ActionTypes.PRESS_HOLD:
                        self.actions[action.body_part][action.action] = action.key_value

            if event.type == KEYUP:

                if event.key in self.key_mapping:

                    action = self.key_mapping[event.key]

                    if action.key_behavior == ActionTypes.PRESS_RELEASE:
                        self.press_state[event.key] = True

                    if action.key_behavior == ActionTypes.PRESS_HOLD:
                        self.press_state[event.key] = True
                        self.actions[action.body_part][action.action] = 0

        return self.actions
