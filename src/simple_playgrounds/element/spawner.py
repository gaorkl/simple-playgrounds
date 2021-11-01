"""
Module for Spawner
"""
import random
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from simple_playgrounds.playgrounds.playground import Playground

from ..agents.agent import Agent
from .element import SceneElement
from ..common.position_utils import CoordinateSampler, Coordinate

from simple_playgrounds.base.entity import Entity
from simple_playgrounds.base.producer import Producer

# pylint: disable=too-many-instance-attributes
# pylint: disable=too-many-arguments


class RandomSpawner(Producer):
    """
    A Spawner produces entities in a random location of the playground.
    """

    def __init__(self,
                 probability: float = 0.05,
                 **kwargs,
                 ):
        """
        Spawner randomly produces a new element in a random part of the Playground.
        The element is temporary, and will disappear upon reset of the Playground.

        Args:
            probability: at each step, probability of creating a new element.
            production_area: PositionAreaSampler.
        """

        Producer.__init__(**kwargs)
        self._probability = probability

    def _is_producing(self) -> bool:
        """
        Tests if the spawner can produce a new element.
        Performs random choice and checks that it is not beyond production limit.

        Returns:
            True if it can produce a new element

        """
        return random.random() < self._probability

    def pre_step(self):
        pass

    def _add_to_playground(self):
        pass

    def _remove_from_playground(self):
        pass
