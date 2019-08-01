import pygame
from pygame.locals import *


class Keyboard():

    def __init__(self, mapping):

        self.mapping = mapping

        self.actions = {}
        available_actions = set([ mapping[k][1] for k in mapping] )
        for act in available_actions:
            self.actions[act] = 0

        self.press_state = {}
        for k in mapping:
            if mapping[k][0] == 'press_once':
                self.press_state[k] = True

    def reset_press_once_actions(self):
        for k in self.mapping:
            if self.mapping[k][0] == 'press_once':
                self.actions[self.mapping[k][1]] = 0

    def get_action(self):

        self.reset_press_once_actions()

        for event in pygame.event.get():

            if event.type == KEYDOWN :

                if event.key in self.mapping:

                    type_event, act, val = self.mapping[event.key]

                    if type_event == 'press_once':
                        self.actions[act] = val
                        self.press_state[event.key] = False

                    elif type_event == 'press_hold':
                        self.actions[act] = val


            if event.type == KEYUP:

                if event.key in self.mapping:

                    type_event, act, val = self.mapping[event.key]

                    if type_event == 'press_once':
                        self.press_state[event.key] = True

                    if type_event == 'press_hold':
                        self.press_state[event.key] = True
                        self.actions[act] = 0



        return self.actions