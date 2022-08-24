"""
Module that defines Base Class SceneElement
"""
from __future__ import annotations
from abc import ABC, abstractmethod
from typing import Optional, TYPE_CHECKING
from simple_playgrounds.entity.physical import PhysicalEntity

if TYPE_CHECKING:
    from simple_playgrounds.common.position_utils import InitCoord
    from simple_playgrounds.playground.playground import Playground


class RewardElement(PhysicalEntity, ABC):
    def __init__(
        self,
        mass: Optional[float] = None,
        traversable: bool = False,
        transparent: bool = False,
        **kwargs,
    ):
        super().__init__(mass, traversable, transparent, **kwargs)

    @property
    @abstractmethod
    def _base_reward(self) -> float:
        ...

    @property
    def reward(self) -> float:
        return self._base_reward


class SceneElement(PhysicalEntity, ABC):
    def __init__(self, **entity_params):
        super().__init__(**entity_params)


class InteractiveElement(SceneElement, ABC):
    pass


class Teleporter(InteractiveElement):
    pass
