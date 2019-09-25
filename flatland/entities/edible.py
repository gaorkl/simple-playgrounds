import pymunk, random, pygame

from .entity import *
from flatland.default_parameters.entities import *

@EntityGenerator.register_subclass('edible')
class Edible(Entity):

    def __init__(self, params):

        params = {**edible_default, **params}

        params['visible'] = True
        params['interactive'] = True

        self.edible = True

        super(Edible, self).__init__(params)

        self.shrink_when_eaten = params['shrink_when_eaten']

        self.reward = params.get('initial_reward', 0)
        self.min_reward = params.get('min_reward', 0)
        self.edible = True

    def activate(self):

        # Change reward, size and mass

        position = self.pm_body.position
        angle = self.pm_body.angle

        self.reward = self.reward*self.shrink_when_eaten


        if self.movable:
            self.mass = self.mass * self.shrink_when_eaten
            inertia = self.compute_moments()
            self.pm_body = pymunk.Body(self.mass, inertia)
            self.pm_body.position = position
            self.pm_body.angle = angle

        if self.physical_shape == 'rectangle':
            self.width = self.width * self.shrink_when_eaten
            self.length = self.length * self.shrink_when_eaten
        else :
            self.radius = self.radius * self.shrink_when_eaten

        if self.physical_shape in ['triangle', 'square', 'pentagon', 'hexagon']:
            self.visible_vertices = self.compute_vertices(self.radius)

        self.generate_pm_visible_shape()
        self.visible_mask = self.generate_visible_mask()

        ##### PyMunk sensor shape
        if self.physical_shape == 'rectangle':
            self.width_interaction = self.width + self.interaction_range
            self.length_interaction = self.length + self.interaction_range

        else:
            self.radius_interaction = self.radius + self.interaction_range

        self.generate_pm_interaction_shape()
        self.interaction_mask = self.generate_interaction_mask()

