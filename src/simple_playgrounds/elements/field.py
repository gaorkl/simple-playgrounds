"""
Module for Field
"""
import random
from typing import Optional, Dict, Tuple, Type, List

from .element import SceneElement
from ..common.position_utils import CoordinateSampler, Coordinate

# pylint: disable=too-many-instance-attributes
# pylint: disable=too-many-arguments


class Field:
    """
    A Field produces entities in a random location of the playground.
    """

    id_number = 0

    def __init__(self,
                 element_produced: Type[SceneElement],
                 production_area: CoordinateSampler,
                 probability: float = 0.05,
                 max_elements_in_playground: int = 10,
                 production_limit: int = 30,
                 entity_produced_params: Optional[Dict] = None):
        """
        Field randomly produces a new SceneElement in a random part of the Playground.
        The SceneElement is temporary, and will disappear upon reset of the Playground.

        Args:
            element_produced: SceneElement produces.
            probability: at each step, probability of creating a new SceneElement.
            max_elements_in_playground: maximum number of SceneElements present in the playground at any given time.
            production_limit: total number of SceneElements that can be produced.
            entity_produced_params: Dictionary of parameters of the SceneElement produced.
            production_area: PositionAreaSampler.

        """

        self.entity_produced = element_produced
        self.location_sampler = production_area

        self.entity_produced_params = {}
        if entity_produced_params:
            self.entity_produced_params = entity_produced_params

        self.probability = probability
        self.limit = max_elements_in_playground
        self.total_limit = production_limit
        self.total_produced = 0
        self.produced_entities: List[SceneElement] = []

        # Internal counter to assign identity number to each entity
        self.name = 'field_' + str(Field.id_number)
        Field.id_number += 1

    def can_produce(self) -> bool:
        """
        Tests if the field can produce a new SceneElement.
        Performs random choice and checks that it is not beyond production limit.

        Returns:
            True if it can produce a new SceneElement

        """

        return (len(self.produced_entities) < self.limit
                and self.total_produced < self.total_limit
                and random.random() < self.probability)

    def produce(self) -> Tuple[SceneElement, Coordinate]:
        """

        Returns: SceneEntity

        """

        obj = self.entity_produced(**self.entity_produced_params)
        obj.temporary = True

        self.total_produced += 1
        self.produced_entities.append(obj)

        initial_position = self.location_sampler.sample()

        return obj, initial_position

    def reset(self):
        """
        Reset the field by resetting the total count of SceneElements produced.
        """

        self.produced_entities = []
        self.total_produced = 0
