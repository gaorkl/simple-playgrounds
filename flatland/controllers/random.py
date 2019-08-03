import pygame
from pygame.locals import *
import random

class Random():

    def __init__(self, actions):

        self.available_actions = actions



    def get_action(self):

        actions = {}

        for act in self.available_actions:

            min_act, max_act, type_act = self.available_actions[act]

            if type_act == 'continuous':

                act_value = random.uniform(min_act, max_act)

            elif type_act == 'discrete':

                act_value = random.choice([min_act, max_act])

            else:

                raise ValueError

            actions[act] = act_value

        return actions