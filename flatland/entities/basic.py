import pymunk, math, pygame
from flatland.utils.config import *
from flatland.default_parameters.entities import *
from flatland.entities.entity import Entity, EntityGenerator

@EntityGenerator.register_subclass('basic')
class Basic(Entity):

    def __init__(self, params ):
        """
        Instantiate an obstacle with the following parameters
        :param pos: 2d tuple or 'random', position of the fruit
        :param environment: the environment calling the creation of the fruit
        """

        params = {**basic_default, **params}
#        params['visible'] = True
#        params['interactive'] = False

        super(Basic, self).__init__(params)

@EntityGenerator.register_subclass('gem')
class Gem(Entity):

    def __init__(self, params ):
        """
        Instantiate an obstacle with the following parameters
        :param pos: 2d tuple or 'random', position of the fruit
        :param environment: the environment calling the creation of the fruit
        """

        params = {**basic_default, **params}
        params['visible'] = True
        params['interactive'] = True

        super(Gem, self).__init__(params)

        self.pm_visible_shape.collision_type = collision_types['gem']

@EntityGenerator.register_subclass('absorbable')
class Absorbable(Entity):

    def __init__(self, params):

        params = { **absorbable_default, **params}
        params['visible'] = True
        params['interactive'] = False

        super(Absorbable, self).__init__(params)

        self.reward = params['reward']
        self.pm_visible_shape.collision_type = collision_types['contact']

        self.absorbable = True

@EntityGenerator.register_subclass('contact_endzone')
class ContactEndZone(Entity):

    def __init__(self, params):

        params = { **contact_endzone_default,**params}
        params['visible'] = True
        params['interactive'] = False

        super(ContactEndZone, self).__init__(params)

        self.reward = params['reward']
        self.pm_visible_shape.collision_type = collision_types['contact']

        self.reward_provided = False

    def pre_step(self):

        self.reward_provided = False

    def get_reward(self):

        if not self.reward_provided:
            self.reward_provided = True
            return self.reward

        else:
            return 0

    def reset(self):
        self.reward_provided = False

        replace = super().reset()

        return replace
