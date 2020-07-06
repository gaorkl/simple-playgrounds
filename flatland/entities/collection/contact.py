from flatland.entities.entity import *


class TerminationContact(Entity):

    entity_type = 'contact_termination'
    visible = True

    def __init__(self, initial_position, default_config_key=None, **kwargs):
        """ Base class for entities that terminate upon contact

        TerminationContact entities generate a termination of the episode and provide a reward to the agent
        in contact with the entity.

        Args:
            initial_position: initial position of the entity. can be list [x,y,theta], AreaPositionSampler or Trajectory
            default_config_key: default configurations, can be visible_endgoal or visible_deathtrap
            **kwargs: other params to configure entity. Refer to Entity class

        Keyword Args:
            reward: Reward provided.
        """

        default_config = self._parse_configuration('contact', default_config_key)
        entity_params = {**default_config, **kwargs}

        super(TerminationContact, self).__init__(initial_position=initial_position, **entity_params)

        self.reward = entity_params['reward']
        self.pm_visible_shape.collision_type = CollisionTypes.CONTACT

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


# @EntityGenerator.register('visible-endgoal')
class VisibleEndGoal(TerminationContact):

    def __init__(self, initial_position, **kwargs):
        """ TerminationContact entity that terminates the episode and provides a positive reward

        Default: Green square of radius 20, reward of 200.

        """

        super(VisibleEndGoal, self).__init__(initial_position=initial_position,
                                             default_config_key='visible_endgoal',
                                             **kwargs)


# @EntityGenerator.register('visible-deathtrap')
class VisibleDeathTrap(TerminationContact):

    def __init__(self, initial_position, **kwargs):
        """ TerminationContact entity that terminates the episode and provides a negative reward

        Default: Red square of radius 20, reward of -200.

        """

        super(VisibleDeathTrap, self).__init__(initial_position=initial_position,
                                               default_config_key='visible_deathtrap',
                                               **kwargs)


class Absorbable(Entity):

    entity_type = 'absorbable'
    absorbable = True

    def __init__(self, initial_position, default_config_key=None, **kwargs):
        """ Base class for entities that are absorbed upon contact

        Absorbable entities provide a reward to the agent upon contact, then disappear from the playground

        Args:
            initial_position: initial position of the entity. can be list [x,y,theta], AreaPositionSampler or Trajectory
            default_config_key: default configurations, can be 'candy' or 'poison'
            **kwargs: other params to configure entity. Refer to Entity class
        """

        default_config = self._parse_configuration('contact', default_config_key)
        entity_params = {**default_config, **kwargs}

        super(Absorbable, self).__init__(initial_position=initial_position, **entity_params)

        self.reward = entity_params['reward']
        self.pm_visible_shape.collision_type = CollisionTypes.CONTACT


# @EntityGenerator.register('candy')
class Candy(Absorbable):

    def __init__(self, initial_position, **kwargs):
        """ Absorbable entity that provides a positive reward

        Default: Violet triangle of radius 4, which provides a reward of 5 when in contact with an agent.

        """

        super(Candy, self).__init__(initial_position=initial_position, default_config_key='candy', **kwargs)


# @EntityGenerator.register('poison')
class Poison(Absorbable):

    def __init__(self, initial_position, **kwargs):
        """ Absorbable entity that provides a negative reward

        Default: Pink pentagon of radius 4, which provides a reward of -5 when in contact with an agent.

        """

        super(Poison, self).__init__(initial_position=initial_position, default_config_key='poison', **kwargs)
