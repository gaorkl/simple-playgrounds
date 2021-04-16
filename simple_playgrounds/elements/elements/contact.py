"""
Contact entities interact upon touching an agent
"""
from abc import ABC
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    pass

from simple_playgrounds.utils.definitions import ElementTypes
from simple_playgrounds.utils.parser import parse_configuration

# pylint: disable=line-too-long
# pylint: disable=useless-super-delegation



class ContactElement(InteractiveElement, ABC):
    """ Base Class for Contact Entities"""


class TerminationContact(ContactSceneElement, ABC):

    """Base class for entities that terminate upon contact"""

    visible = True
    terminate_upon_contact = True

    def __init__(self, **kwargs):
        """
        TerminationContact terminate the Episode upon contact with an Agent.
        Provides a reward to the agent.

        Args:
            **kwargs: other params to configure SceneElement. Refer to Entity class.

        Keyword Args:
            reward: Reward provided.
        """

        default_config = parse_configuration('element_contact', self.entity_type)
        entity_params = {**default_config, **kwargs}

        super().__init__(**entity_params)
        self.reward = entity_params['reward']


class VisibleEndGoal(TerminationContact):
    """ TerminationContact terminates the episode and provides a positive reward.

    Default: Green square of radius 20, reward of 200.

    """
    entity_type = ElementTypes.VISIBLE_ENDGOAL


class VisibleDeathTrap(TerminationContact):

    """ TerminationContact that terminates the episode and provides a negative reward.

    Default: Red square of radius 20, reward of -200.

    """
    entity_type = ElementTypes.VISIBLE_DEATHTRAP


class Absorbable(ContactSceneElement, ABC):

    """Base class for entities that are absorbed upon contact."""

    absorbable = True

    def __init__(self, **kwargs):
        """
        Absorbable entities provide a reward to the agent upon contact,
        then disappears from the playground.

        Args:
            **kwargs: other params to configure SceneElement. Refer to Entity class.
        """

        default_config = parse_configuration('element_contact', self.entity_type)
        entity_params = {**default_config, **kwargs}

        super().__init__(**entity_params)
        self.reward = entity_params['reward']

    def activate_by_contact(self):

        list_add = []
        list_remove = [self]

        return list_remove, list_add


class Candy(Absorbable):
    """ Absorbable entity that provides a positive reward.

    Default: Violet triangle of radius 4, which provides a reward of 5 when in contact with an agent.

    """
    entity_type = ElementTypes.CANDY


class Poison(Absorbable):
    """ Absorbable entity that provides a negative reward

    Default: Pink pentagon of radius 4, which provides a reward of -5 when in contact with an agent.

    """

    entity_type = ElementTypes.POISON


class PushButton(ContactSceneElement):
    """Push button used to open a door."""

    entity_type = ElementTypes.SWITCH
    background = False

    def __init__(self, door, **kwargs):
        """
        Opens a door when in contact with an agent.
        Default: Pale brown square of size 10.

        Args:
            door: Door opened by the switch.
            **kwargs: other params to configure SceneElement. Refer to Entity class.
        """

        default_config = parse_configuration('element_interactive', self.entity_type)
        entity_params = {**default_config, **kwargs}

        super().__init__(**entity_params)

        self.door = door

    def activate_by_contact(self):
        elems_remove = [self, self.door]
        list_add = []

        self.door.opened = True

        return list_remove, list_add
