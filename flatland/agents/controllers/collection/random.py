import pygame
from pygame.locals import *
import random

from flatland.agents.controllers.controller import ControllerGenerator, Controller

@ControllerGenerator.register_subclass('random')
class Random(Controller):

    def __init__(self, controller_params):

        super(Random).__init__(controller_params)
        self.require_key_mapping = False
        self.actions = {}

    def set_available_actions(self, available_actions):

        self.available_actions = available_actions
        for act in available_actions:
            self.actions[act] = 0

    def get_actions(self):

        for act in self.available_actions:

            min_act, max_act, type_act = self.available_actions[act]

            if type_act == 'continuous':

                act_value = random.uniform(min_act, max_act)

            elif type_act == 'discrete':

                act_value = random.choice([min_act, max_act])

            else:

                raise ValueError

            self.actions[act] = act_value

        return self.actions

