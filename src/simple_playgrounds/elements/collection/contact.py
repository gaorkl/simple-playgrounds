"""
Contact entities interact upon touching an agent
"""
from abc import ABC

from ..element import ContactElement
from simple_playgrounds.common.definitions import ElementTypes
from ...configs.parser import parse_configuration


# pylint: disable=line-too-long
# pylint: disable=useless-super-delegation


class TerminationContact(ContactElement, ABC):
    """Base class for entities that terminate upon contact"""
    def __init__(self, config_key, **kwargs):
        """
        TerminationContact terminate the Episode upon contact with an Agent.
        Provides a reward to the agent.

        Args:
            **kwargs: other params to configure SceneElement. Refer to Entity class.

        Keyword Args:
            reward: Reward provided.
        """

        default_config = parse_configuration('element_contact', config_key)
        entity_params = {**default_config, **kwargs}

        super().__init__(**entity_params)

    @property
    def terminate_upon_activation(self):
        return True

    def activate(self, activator):
        return None, None


class VisibleEndGoal(TerminationContact):
    """ TerminationContact terminates the episode and provides a positive reward.

    Default: Green square of radius 20, reward of 200.

    """
    def __init__(self, reward: float = 200, **kwargs):

        super().__init__(ElementTypes.VISIBLE_ENDGOAL, reward=reward, **kwargs)


class VisibleDeathTrap(TerminationContact):
    """ TerminationContact that terminates the episode and provides a negative reward.

    Default: Red square of radius 20, reward of -200.

    """
    def __init__(self, reward: float = -200, **kwargs):
        super().__init__(ElementTypes.VISIBLE_DEATHTRAP,
                         reward=reward,
                         **kwargs)


class Absorbable(ContactElement, ABC):
    def __init__(self, config_key, **kwargs):
        """
        Absorbable entities provide a reward to the agent upon contact,
        then disappears from the playground.

        Args:
            **kwargs: other params to configure SceneElement. Refer to Entity class.
        """

        default_config = parse_configuration('element_contact', config_key)
        entity_params = {**default_config, **kwargs}

        super().__init__(**entity_params)

    def activate(self, activator):

        list_add = None
        list_remove = [self]

        return list_remove, list_add

    @property
    def terminate_upon_activation(self):
        return False


class Candy(Absorbable):
    """ Absorbable entity that provides a positive reward.

    Default: Violet triangle of radius 4, which provides a reward of 5 when in contact with an agent.

    """
    def __init__(self, reward: float = 5, **kwargs):

        assert reward > 0

        super().__init__(ElementTypes.CANDY, reward=reward, **kwargs)


class Poison(Absorbable):
    """ Absorbable entity that provides a negative reward

    Default: Pink pentagon of radius 4, which provides a reward of -5 when in contact with an agent.

    """
    def __init__(self, reward: float = -5, **kwargs):

        super().__init__(ElementTypes.POISON, reward=reward, **kwargs)


#
# class PushButton(ContactElement):
#     """Push button used to open a door."""
#
#     entity_type = ElementTypes.SWITCH
#     background = False
#
#     def __init__(self, door, **kwargs):
#         """
#         Opens a door when in contact with an agent.
#         Default: Pale brown square of size 10.
#
#         Args:
#             door: Door opened by the switch.
#             **kwargs: other params to configure SceneElement. Refer to Entity class.
#         """
#
#         default_config = parse_configuration('element_interactive', self.entity_type)
#         entity_params = {**default_config, **kwargs}
#
#         super().__init__(**entity_params)
#
#         self.door = door
#
#     def activate_by_contact(self):
#         elems_remove = [self, self.door]
#         list_add = []
#
#         self.door.opened = True
#
#         return list_remove, list_add
