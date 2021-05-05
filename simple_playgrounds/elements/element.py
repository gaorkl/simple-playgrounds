"""
Module that defines Base Class SceneElement
"""

from typing import Union, Tuple, Optional
from simple_playgrounds.common.timer import Timer
from simple_playgrounds.common.position_utils import CoordinateSampler, Coordinate
from simple_playgrounds.configs import parse_configuration
from simple_playgrounds.definitions import CollisionTypes

from abc import ABC, abstractmethod

from simple_playgrounds.common.entity import Entity
from simple_playgrounds.agents import Agent


class SceneElement(Entity, ABC):
    def __init__(self, **entity_params):
        super().__init__(**entity_params)


class TeleportElement(SceneElement, ABC):
    """ Base Class for Teleport Entities"""
    def __init__(
        self,
        config_key,
        destination: Union[Coordinate, CoordinateSampler, SceneElement],
        **entity_params,
    ):

        default_config = parse_configuration('element_teleport', config_key)
        entity_params = {**default_config, **entity_params}

        super().__init__(**entity_params)

        self.destination = destination

    @abstractmethod
    def energize(self, agent: Agent):
        pass


class GemElement(SceneElement, ABC):
    """
    A Gem interacts with other SceneElements.
    """
    def __init__(self, config_key, elem_activated, **entity_params):

        default_config = parse_configuration('element_gem', config_key)
        entity_params = {**default_config, **entity_params}

        SceneElement.__init__(self,
                              visible_shape=True,
                              invisible_shape=False,
                              **entity_params)

        self.elem_activated = elem_activated

    def _set_shape_collision(self):
        self.pm_visible_shape.collision_type = CollisionTypes.GEM


class InteractiveElement(SceneElement, ABC):
    """Base Class for Interactive Elements"""
    def __init__(self, reward: float = 0, **entity_params):

        SceneElement.__init__(self, **entity_params)

        # Initialize reward
        self.reward = reward
        self._reward_provided: bool = False

        # Element activated
        self.activated = False

    def pre_step(self):
        self._reward_provided = False
        self.activated = False

    @property
    def reward(self):
        """ Reward provided upon contact."""

        if not self._reward_provided:
            self._reward_provided = True
            return self._reward

        return 0

    @reward.setter
    def reward(self, rew: float):
        self._reward = rew

    @abstractmethod
    def activate(self, activator: Union[Agent, GemElement, Timer]):
        self.activated = True

    @property
    @abstractmethod
    def terminate_upon_activation(self):
        ...


class ContactElement(InteractiveElement, ABC):
    """ Base Class for Contact Entities"""
    def __init__(self, **entity_params):

        InteractiveElement.__init__(self,
                                    visible_shape=True,
                                    invisible_shape=False,
                                    **entity_params)

    def _set_shape_collision(self):
        self.pm_visible_shape.collision_type = CollisionTypes.CONTACT


class ZoneElement(InteractiveElement, ABC):
    """ Base Class for Contact Entities"""
    def __init__(self, **entity_params):

        InteractiveElement.__init__(self,
                                    visible_shape=False,
                                    invisible_shape=True,
                                    **entity_params)

    def _set_shape_collision(self):
        self.pm_invisible_shape.collision_type = CollisionTypes.CONTACT
