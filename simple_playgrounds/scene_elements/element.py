"""
Module that defines Base Class SceneElement
"""

from typing import Union, Tuple, TYPE_CHECKING
if TYPE_CHECKING:
    from simple_playgrounds.utils.definitions import AddRemoveElems

from abc import ABC, abstractmethod

from simple_playgrounds.entity import Entity
from simple_playgrounds.utils.definitions import ElementTypes, CollisionTypes
from simple_playgrounds.utils.parser import parse_configuration


class SceneElement(Entity, ABC):
    pass


class BasicElement(SceneElement):
    """ Basic Scene elements are non-interactive obstacles."""
    visible = True


class InteractiveElement(SceneElement, ABC):
    """Base Class for Interactive Elements"""
    interactive = True
    terminate_upon_activation = False

    def __init__(self, reward, **entity_params):

        super(SceneElement).__init__(**entity_params)

        # Initialize reward
        self.reward = reward
        self.reward_provided = False

        # assign collision shape
        self.assign_collision_to_shape()

    def pre_step(self):
        self.reward_provided = False

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

    @abstractmethod
    def assign_collision_to_shape(self):
        ...

    @abstractmethod
    def activate(self,
                 entity: Union[None, Entity] = None,
                 ) -> AddRemoveElems:
        """
        Activate the SceneElement.

        Args:
            entity: Entity that activated the SceneElement.

        Returns:
            TODO
        """
        ...


class ContactElement(InteractiveElement, ABC):
    """ Base Class for Contact Entities"""

    pass



class Activable(InteractiveElement):

    def __init__(self, **kwargs):

        default_config = parse_configuration('element_interactive', self.entity_type)
        entity_params = {**default_config, **kwargs}

        super().__init__(**entity_params)

        self.pm_interaction_shape.collision_type = CollisionTypes.INTERACTIVE

        self.reward = entity_params['reward']

        self.reward_provided = False

    def pre_step(self):
        super().pre_step()
        self.reward_provided = False

    @property
    def reward(self):

        if not self.reward_provided:
            self.reward_provided = True
            return self._reward

        return 0

    @reward.setter
    def reward(self, rew):
        self._reward = rew

    def activate_by_element(self, activating_element):
        # pylint: disable=useless-super-delegation
        return super().activate_by_element(activating_element)