"""
Module for Spawner
"""
from __future__ import annotations

import random
from typing import TYPE_CHECKING, Dict, List, Optional, Tuple, Type

from ..element import SceneElement
from ..utils.position import Coordinate, CoordinateSampler

if TYPE_CHECKING:
    from ..playground import Playground

# pylint: disable=too-many-instance-attributes
# pylint: disable=too-many-arguments


class Spawner:
    """
    A Spawner produces entities in a random location of the playground.
    """

    id_number = 0

    def __init__(
        self,
        element_produced: Type[SceneElement],
        production_area: CoordinateSampler,
        probability: float = 0.05,
        max_elements_in_playground: int = 10,
        production_limit: int = 30,
        entity_produced_params: Optional[Dict] = None,
        allow_overlapping: bool = True,
    ):
        """
        Spawner randomly produces a new element in a random part of the Playground.
        The element is temporary, and will disappear upon reset of the Playground.

        Args:
            element_produced: SceneElement produces.
            probability: at each step, probability of creating a new element.
            max_elements_in_playground: maximum number of element present
                in the playground at any given time.
            production_limit: total number of elements that can be produced.
            entity_produced_params: Dictionary of parameters of the element produced.
            production_area: PositionAreaSampler.
            allow_overlapping: allow overlapping for spawned entities.

        """

        self.entity_produced = element_produced
        self.location_sampler = production_area

        self.entity_produced_params = {}
        if entity_produced_params:
            self.entity_produced_params = entity_produced_params

        self.entity_produced_params["temporary"] = True
        self.probability = probability
        self.limit = max_elements_in_playground
        self.total_limit = production_limit
        self.total_produced = 0
        self.produced_entities: List[SceneElement] = []
        self.allow_overlapping = allow_overlapping

        # Internal counter to assign identity number to each entity
        self.name = "spawner_" + str(Spawner.id_number)
        Spawner.id_number += 1

        self._playground: Optional[Playground] = None

    @property
    def playground(self):
        return self._playground

    @playground.setter
    def playground(self, pg):
        self._playground = pg

    @property
    def in_playground(self):
        return bool(self._playground)

    def _can_produce(self) -> bool:
        """
        Tests if the spawner can produce a new element.
        Performs random choice and checks that it is not beyond production limit.

        Returns:
            True if it can produce a new element

        """

        return (
            len(self.produced_entities) < self.limit
            and self.total_produced < self.total_limit
            and random.random() < self.probability
        )

    def produce(
        self,
    ) -> Optional[Tuple[SceneElement, Coordinate]]:
        """

        Returns: A list of SceneElement or Agent, initial position

        """

        if self._can_produce():
            obj = self.entity_produced(**self.entity_produced_params)

            self.total_produced += 1
            self.produced_entities.append(obj)

            initial_position = self.location_sampler.sample()

            return (obj, initial_position)

        return None

    def reset(self):
        """
        Reset the spawner by resetting the total count of elements produced.
        """

        self.produced_entities = []
        self.total_produced = 0
