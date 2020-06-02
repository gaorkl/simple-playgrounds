import pygame
from pygame.locals import *
import random
from flatland.utils.config import *


from flatland.agents.controllers.controller import ControllerGenerator, Controller

@ControllerGenerator.register_subclass('random')
class Random(Controller):

    def __init__(self):


        self.controller_type = 'random'
        super().__init__()
        self.require_key_mapping = False
        self.actions = {}

    def get_actions(self):

        for action in self.available_actions:

            if action.action_type == ActionTypes.CONTINUOUS:

                act_value = random.uniform(action.min, action.max)

            elif action.action_type == ActionTypes.DISCRETE:

                act_value = random.choice([action.min, action.max])

            else:

                raise ValueError

            self.actions[action.body_part][action.action] = act_value

        return self.actions

