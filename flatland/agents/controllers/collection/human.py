import pygame
from pygame.locals import *
from flatland.agents.controllers.controller import ControllerGenerator, Controller


@ControllerGenerator.register_subclass('keyboard')
class Keyboard(Controller):

    def __init__(self, controller_params):

        super().__init__()

        self.key_mapping = controller_params.get('key_mapping', {} )
        self.require_key_mapping = True
        self.press_state = {}

    def assign_key_mapping(self, default_key_mapping):
        self.key_mapping = {**self.key_mapping, **default_key_mapping}

        for k in self.key_mapping:
            if self.key_mapping[k][0] == 'press_once':
                self.press_state[k] = True

    def set_available_actions(self, available_actions):

        self.available_actions = available_actions
        for act in available_actions:
            self.actions[act] = 0

    def reset_press_once_actions(self):
        for k in self.key_mapping:
            if self.key_mapping[k][0] == 'press_once':
                self.actions[self.key_mapping[k][1]] = 0

    def get_actions(self):

        self.reset_press_once_actions()

        for event in pygame.event.get():

            if event.type == KEYDOWN:

                if event.key in self.key_mapping:

                    type_event, act, val = self.key_mapping[event.key]

                    if type_event == 'press_once':
                        self.actions[act] = val
                        self.press_state[event.key] = False

                    elif type_event == 'press_hold':
                        self.actions[act] = val

            if event.type == KEYUP:

                if event.key in self.key_mapping:

                    type_event, act, val = self.key_mapping[event.key]

                    if type_event == 'press_once':
                        self.press_state[event.key] = True

                    if type_event == 'press_hold':
                        self.press_state[event.key] = True
                        self.actions[act] = 0

        return self.actions
