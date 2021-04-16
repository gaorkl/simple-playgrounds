"""
Module that defines Base Class SceneElement
"""

from typing import Union, Tuple
from simple_playgrounds.utils.position_utils import CoordinateSampler, Trajectory

from abc import ABC, abstractmethod

from simple_playgrounds.entity import Entity
from simple_playgrounds.agents import Agent


InitCoord = Union[
    None,
    Tuple[Tuple[float, float], float],
    CoordinateSampler,
    Trajectory,
]


class SceneElement(Entity, ABC):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)


# INTERACTIVE ELEMENT


class InteractiveElement(SceneElement, ABC):
    """Base Class for Interactive Elements"""

    def __init__(self, reward: float, **kwargs):

        super(SceneElement).__init__(**kwargs)

        # Initialize reward
        self.reward = reward
        self._reward_provided: bool = False

        # Single Activation per step

    def pre_step(self):
        self._reward_provided = False

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
    def activate(self):
        ...

    @property
    @abstractmethod
    def terminate_upon_activation(self):
        ...


# TELEPORT ELEMENTS


class TeleportElement(SceneElement, ABC):
    """ Base Class for Contact Entities"""

    def __init__(self,
                 target: Union[InitCoord, SceneElement],
                 **kwargs,
                 ):

        super().__init__(**kwargs)
        self.target = target

    @abstractmethod
    def energize(self, agent: Agent):
        pass


#
        # if teleport.target.traversable:
        #     agent.position = teleport.target.position
        #
        # else:
        #     area_shape = teleport.target.physical_shape
        #     if area_shape == 'rectangle':
        #         width = teleport.target.width + agent.base_platform.radius * 2 + 1
        #         length = teleport.target.length + agent.base_platform.radius * 2 + 1
        #         angle = teleport.target.angle
        #         sampler = CoordinateSampler(
        #             center=teleport.target.position,
        #             area_shape=area_shape,
        #             angle=angle,
        #             width_length=[width + 2, length + 2],
        #             excl_width_length=[width, length],
        #         )
        #     else:
        #         radius = teleport.target.radius + agent.base_platform.radius + 1
        #         sampler = CoordinateSampler(
        #             center=teleport.target.position,
        #             area_shape='circle',
        #             radius=radius,
        #             excl_radius=radius,
        #         )
        #
        #     agent.coordinates = sampler.sample()
        #
