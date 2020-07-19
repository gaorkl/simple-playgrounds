"""
Contact entities interact upon touching an agent
"""
from abc import ABC, abstractmethod

from simple_playgrounds.entities.scene_elements.element import SceneElement
from simple_playgrounds.utils.definitions import CollisionTypes

#pylint: disable=line-too-long
#pylint: disable=useless-super-delegation

class ContactSceneElement(SceneElement, ABC):
    """ Base Class for Contact Entities"""
    def __init__(self, **kwargs):

        SceneElement.__init__(self, **kwargs)
        self.pm_visible_shape.collision_type = CollisionTypes.CONTACT

        self.reward = 0
        self.reward_provided = False

    def pre_step(self):
        self.reward_provided = False

    @abstractmethod
    def activate(self):
        """
        Upon activation, returns a list of entity to remove from PLayground,
        and a list of entities to add to Playground.
        """
        list_remove = []
        list_add = []

        return list_remove, list_add

    @property
    def reward(self):
        """ Reward provided upon contact."""

        if not self.reward_provided:
            self.reward_provided = True
            return self._reward

        return 0

    @reward.setter
    def reward(self, rew):
        self._reward = rew


class TerminationContact(ContactSceneElement):

    """Base class for entities that terminate upon contact"""

    entity_type = 'contact_termination'
    visible = True
    terminate_upon_contact = True

    def __init__(self, initial_position, default_config_key=None, **kwargs):
        """
        TerminationContact terminate the Episode upon contact with an Agent.
        Provides a reward to the agent.

        Args:
            initial_position: initial position of the SceneElement.
                Can be list [x,y,theta], AreaPositionSampler or Trajectory.
            default_config_key: default configurations, can be visible_endgoal or visible_deathtrap
            **kwargs: other params to configure SceneElement. Refer to Entity class.

        Keyword Args:
            reward: Reward provided.
        """

        default_config = self._parse_configuration('contact', default_config_key)
        entity_params = {**default_config, **kwargs}

        super().__init__(initial_position=initial_position, **entity_params)
        self.reward = entity_params['reward']

    def activate(self):
        return super().activate()


class VisibleEndGoal(TerminationContact):
    """ TerminationContact terminates the episode and provides a positive reward.

    Default: Green square of radius 20, reward of 200.

    """

    def __init__(self, initial_position, **kwargs):

        super(VisibleEndGoal, self).__init__(initial_position=initial_position,
                                             default_config_key='visible_endgoal',
                                             **kwargs)


class VisibleDeathTrap(TerminationContact):

    """ TerminationContact that terminates the episode and provides a negative reward.

    Default: Red square of radius 20, reward of -200.

    """
    def __init__(self, initial_position, **kwargs):

        super(VisibleDeathTrap, self).__init__(initial_position=initial_position,
                                               default_config_key='visible_deathtrap',
                                               **kwargs)


class Absorbable(ContactSceneElement):

    """Base class for entities that are absorbed upon contact."""

    entity_type = 'absorbable'
    absorbable = True

    def __init__(self, initial_position, default_config_key=None, **kwargs):
        """
        Absorbable entities provide a reward to the agent upon contact,
        then disappears from the playground.

        Args:
            initial_position: initial position of the SceneElement.
                Can be list [x,y,theta], AreaPositionSampler or Trajectory.
            default_config_key: default configurations, can be 'candy' or 'poison'.
            **kwargs: other params to configure SceneElement. Refer to Entity class.
        """

        default_config = self._parse_configuration('contact', default_config_key)
        entity_params = {**default_config, **kwargs}

        super(Absorbable, self).__init__(initial_position=initial_position, **entity_params)
        self.reward = entity_params['reward']

    def activate(self):

        list_add = []
        list_remove = [self]

        return list_remove, list_add


class Candy(Absorbable):
    """ Absorbable entity that provides a positive reward.

    Default: Violet triangle of radius 4, which provides a reward of 5 when in contact with an agent.

    """
    def __init__(self, initial_position, **kwargs):

        super(Candy, self).__init__(initial_position=initial_position, default_config_key='candy', **kwargs)


class Poison(Absorbable):
    """ Absorbable entity that provides a negative reward

    Default: Pink pentagon of radius 4, which provides a reward of -5 when in contact with an agent.

    """

    def __init__(self, initial_position, **kwargs):

        super(Poison, self).__init__(initial_position=initial_position, default_config_key='poison', **kwargs)


class PushButton(ContactSceneElement):
    """Push button used to open a door."""
    entity_type = 'pushbutton'

    def __init__(self, initial_position, door, **kwargs):
        """
        Opens a door when in contact with an agent.
        Default: Pale brown square of size 10.

        Args:
            initial_position: initial position of the entity.
                Can be list [x,y,theta], AreaPositionSampler or Trajectory.
            door: Door opened by the switch.
            **kwargs: other params to configure SceneElement. Refer to Entity class.
        """

        default_config = self._parse_configuration('interactive', 'switch')
        entity_params = {**default_config, **kwargs}

        super(PushButton, self).__init__(initial_position=initial_position, **entity_params)

        self.door = door

    def activate(self):
        list_remove = [self, self.door]
        list_add = []

        self.door.opened = True

        return list_remove, list_add
