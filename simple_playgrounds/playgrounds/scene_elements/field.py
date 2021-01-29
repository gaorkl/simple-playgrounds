"""
Module for Field
"""
import random
from simple_playgrounds.utils import SceneElementTypes

#pylint: disable=too-many-instance-attributes
#pylint: disable=too-many-arguments

class Field:
    """
    A Field produces entities in a random location of the playground.
    """

    id_number = 0
    entity_type = SceneElementTypes.FIELD

    def __init__(self, entity_produced, production_area, probability=0.05, limit=10, total_limit=30,
                 entity_produced_params=None):
        """
        Field randomly produces a new SceneElement in a random part of the Playground.
        The SceneElement is temporary, and will disappear upon reset of the Playground.

        Args:
            entity_produced: SceneElement produces.
            probability: at each step, probability of creating a new SceneElement.
            limit: maximum number of SceneElements present in the playground at any given time.
            total_limit: total number of SceneElements that can be produced.
            entity_produced_params: Dictionary of parameters of the SceneElement produced.
            production_area: PositionAreaSampler.

        """

        self.entity_produced = entity_produced
        self.location_sampler = production_area

        if entity_produced_params is None:
            self.entity_produced_params = {}
        else:
            self.entity_produced_params = entity_produced_params

        self.probability = probability
        self.limit = limit
        self.total_limit = total_limit
        self.total_produced = 0
        self.produced_entities = []

        # Internal counter to assign identity number to each entity
        self.name = 'field_' + str(Field.id_number)
        Field.id_number += 1


    def can_produce(self):
        """
        Tests if the field can produce a new SceneElement.
        Performs random choice and checks that it is not beyond production limit.

        Returns:
            True if it can produce a new SceneElement

        """

        return len(self.produced_entities) < self.limit \
               and self.total_produced < self.total_limit\
               and random.random() < self.probability

    def produce(self):
        """

        Returns: SceneEntity

        """

        obj = self.entity_produced(initial_position=self.location_sampler,
                                   **self.entity_produced_params)
        obj.is_temporary_entity = True

        self.total_produced += 1
        self.produced_entities.append(obj)

        return obj

    def reset(self):
        """
        Reset the field by resetting the total count of SceneElements produced.
        """

        self.produced_entities = []
        self.total_produced = 0
