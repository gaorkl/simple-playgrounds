"""
Module that defines Base Class SceneElement
"""
from abc import ABC, abstractmethod
from typing import List, Optional, Tuple

from ..common.entity import Entity
from ..common.position_utils import InitCoord


class SceneElement(Entity, ABC):
    def __init__(self, **entity_params):
        super().__init__(**entity_params)


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
        super().pre_step()
        self._reward_provided = False
        self.activated = False

    @property
    def reward(self) -> float:
        """ Reward provided upon contact."""

        if not self._reward_provided:
            self._reward_provided = True
            return self._reward

        return 0

    @reward.setter
    def reward(self, rew: float):
        self._reward = rew

    @abstractmethod
    def activate(
        self,
        activator,
    ) -> Tuple[Optional[List[SceneElement]], Optional[List[Tuple[SceneElement,
                                                                 InitCoord]]]]:
        ...

    @property
    @abstractmethod
    def terminate_upon_activation(self) -> bool:
        ...
