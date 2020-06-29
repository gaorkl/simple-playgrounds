from abc import ABC, abstractmethod
import random
from flatland.utils.config import ActionTypes, KeyTypes

class Controller(ABC):

    def __init__(self):

        self.require_key_mapping = False
        self.available_actions = []
        self.null_actions = {}

    @abstractmethod
    def generate_actions(self):
        pass

    def generate_null_actions_dict(self):

        actions = {}
        for action in self.available_actions:
            actions[action.body_part] = {}

        for action in self.available_actions:
            actions[action.body_part][action.action] = 0

        return actions

#
# class BaseController(Controller):
#     def __init__(self, controller_params):
#
#         super().__init__(controller_params)


class Random(Controller):

    controller_type = 'random'

    def __init__(self, available_actions):

        super().__init__()
        self.available_actions = available_actions
        self.null_actions = self.generate_null_actions_dict()

    def generate_actions(self):

        actions = self.null_actions.copy()

        for action in self.available_actions:

            if action.action_type == ActionTypes.CONTINUOUS:
                act_value = random.uniform(action.min, action.max)

            elif action.action_type == ActionTypes.DISCRETE:
                act_value = random.choice([action.min, action.max])

            else:
                raise ValueError

            actions[action.body_part][action.action] = act_value

        return actions

import pygame
from pygame.locals import *


class Keyboard(Controller):

    controller_type = 'keyboard'

    def __init__(self, available_actions, key_mapping):

        super().__init__()

        self.require_key_mapping = True
        self.press_state = {}
        self.available_actions = available_actions
        self.key_mapping = key_mapping

        self.actions = self.generate_null_actions_dict()

    # def set_available_actions(self, available_actions):
    #
    #     super().set_available_actions(available_actions)
    #
    #     self.assign_key_mapping(available_actions)

    @property
    def key_mapping(self):

        return self._key_mapping

    @key_mapping.setter
    def key_mapping(self, keymap):

        self._key_mapping = {}

        for action in keymap:

            if action.key in self._key_mapping:
                raise ValueError('Key assigned twice ')

            self._key_mapping[action.key] = action

            if action.key_behavior == KeyTypes.PRESS_RELEASE:
                self.press_state[action.key_behavior] = True

    def reset_press_once_actions(self):

        for k, action in self.key_mapping.items():

            if action.key_behavior == KeyTypes.PRESS_RELEASE:
                self.actions[action.body_part][action.action] = 0

    def generate_actions(self):

        self.reset_press_once_actions()

        for event in pygame.event.get():

            if event.type == KEYDOWN:

                if event.key in self.key_mapping:

                    action = self.key_mapping[event.key]

                    if action.key_behavior == KeyTypes.PRESS_RELEASE:
                        self.actions[action.body_part][action.action] = action.key_value
                        self.press_state[event.key] = False

                    elif action.key_behavior == KeyTypes.PRESS_HOLD:
                        self.actions[action.body_part][action.action] = action.key_value

            if event.type == KEYUP:

                if event.key in self.key_mapping:

                    action = self.key_mapping[event.key]

                    if action.key_behavior == KeyTypes.PRESS_RELEASE:
                        self.press_state[event.key] = True

                    if action.key_behavior == KeyTypes.PRESS_HOLD:
                        self.press_state[event.key] = True
                        self.actions[action.body_part][action.action] = 0

        return self.actions

