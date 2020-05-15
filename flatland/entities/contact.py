from flatland.utils.config import *
from flatland.entities.entity import Entity



class TerminationContact(Entity):

    entity_type = 'contact_termination'
    visible = True


    def __init__(self, initial_position, default_config_key=None, **kwargs):
        """
        
        :param position: initial position or position samples
        :param default_config_key: visible_endgoal or visible_deathtrap
        :param kwargs: other params
        """

        default_config = self.parse_configuration('contact', default_config_key)
        entity_params = {**default_config, **kwargs}

        super(TerminationContact, self).__init__(initial_position = initial_position, **entity_params)

        self.reward = entity_params['reward']
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
        super().reset()



class VisibleEndGoal(TerminationContact):

    def __init__(self, initial_position, **kwargs):

        super(VisibleEndGoal, self).__init__(initial_position=initial_position, default_config_key='visible_endgoal', **kwargs)


class VisibleDeathTrap(TerminationContact):

    def __init__(self, initial_position, **kwargs):

        super(VisibleDeathTrap, self).__init__(initial_position=initial_position, default_config_key='visible_deathtrap', **kwargs)



class Absorbable(Entity):

    entity_type = 'absorbable'
    absorbable = True

    def __init__(self, initial_position, default_config_key = None, **kwargs):
        """

        :param position: initial position
        :param default_config_key: pellet or poison
        :param kwargs: other params
        """

        default_config = self.parse_configuration('contact', default_config_key)
        entity_params = {**default_config, **kwargs}

        super(Absorbable, self).__init__(initial_position = initial_position, **entity_params)

        self.reward = entity_params['reward']
        self.pm_visible_shape.collision_type = collision_types['contact']

class Candy(Absorbable):

    def __init__(self, initial_position, **kwargs):

        super(Candy, self).__init__(initial_position=initial_position, default_config_key='candy', **kwargs)


class Poison(Absorbable):

    def __init__(self, initial_position, **kwargs):

        super(Poison, self).__init__(initial_position=initial_position, default_config_key='poison', **kwargs)



