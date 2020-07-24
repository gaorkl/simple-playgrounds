"""
Module defining Controllers.
Controllers are used to chose actions for agents.
"""
from abc import ABC, abstractmethod
import random

import pygame
from pygame.locals import *

from simple_playgrounds.utils.definitions import ActionTypes, KeyTypes


class Controller(ABC):
    """ Base Class for Controllers."""

    def __init__(self):

        self.require_key_mapping = False
        self.null_actions = []
        self.actions = []

    @property
    def available_actions(self):
        """
        Dictionary of available actions.
        """
        return self._available_actions

    @available_actions.setter
    def available_actions(self, act):
        self._available_actions = act
        self.actions = self.generate_null_actions_dict()
        self.null_actions = self.generate_null_actions_dict()

    @abstractmethod
    def generate_actions(self):
        """ Generate actions for each part of an agent,
        Returns a dictionary of parts and associated actions,
        """

    def generate_null_actions_dict(self):
        """ Generates a dictionary of null actions."""
        actions = {}
        for action in self.available_actions:
            actions[action.body_part] = {}

        for action in self.available_actions:
            actions[action.body_part][action.action] = 0

        return actions


class External(Controller):

    def generate_actions(self):

        pass

class Random(Controller):
    """
    A random controller picks actions randomly.
    If the action is continuous, it picks the action using a uniform distribution.
    If the aciton is discrete (binary), it picks a random action.
    """
    controller_type = 'random'

    def generate_actions(self):

        actions = self.null_actions.copy()

        for action in self.available_actions:

            if action.action_type == ActionTypes.CONTINUOUS_CENTERED:
                act_value = random.uniform(action.min, action.max)

            elif action.action_type == ActionTypes.CONTINUOUS_NOT_CENTERED:
                act_value = random.uniform(action.min, action.max)

            elif action.action_type == ActionTypes.DISCRETE:
                act_value = random.choice([action.min, action.max])

            else:
                raise ValueError

            actions[action.body_part][action.action] = act_value

        return actions


class Keyboard(Controller):
    """
    Keyboard controller require that a keymapping is defined in the agent.
    The keymapping should be assigned to the controller.
    """
    controller_type = 'keyboard'

    def __init__(self):

        super().__init__()

        self.require_key_mapping = True
        self.press_state = {}
        self.key_mapping = None

    @property
    def key_mapping(self):
        """ Key mapping that links keyboard strokes with a desired action."""
        return self._key_mapping

    @key_mapping.setter
    def key_mapping(self, keymap):

        if keymap is None:
            keymap = []

        self._key_mapping = {}

        for action in keymap:

            if action.key in self._key_mapping:
                raise ValueError('Key assigned twice ')

            self._key_mapping[action.key] = action

            if action.key_behavior == KeyTypes.PRESS_RELEASE:
                self.press_state[action.key_behavior] = True

    def _reset_press_once_actions(self):

        for _, action in self.key_mapping.items():

            if action.key_behavior == KeyTypes.PRESS_RELEASE:
                self.actions[action.body_part][action.action] = 0

    def generate_actions(self):

        # pylint: disable=undefined-variable

        self._reset_press_once_actions()

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
