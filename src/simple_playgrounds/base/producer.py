from abc import ABC, abstractmethod
from typing import Dict, Type, Optional, List, TYPE_CHECKING

if TYPE_CHECKING:
    from simple_playgrounds.common.position_utils import CoordinateSampler

from simple_playgrounds.base.entity import Entity


class Producer(Entity, ABC):

    def __init__(self,
                 production_area: CoordinateSampler,
                 entity_produced: Type[Entity],
                 limit_entities_in_playground: Optional[int] = None,
                 total_production_limit: Optional[int] = None,
                 entity_produced_params: Optional[Dict] = None,
                 allow_overlapping: bool = True,
                 **kwargs,
                 ):

        """

        Args:
            entity_produced: Entity produced. Can be agents, scene elements, etc..
            limit_entities_in_playground: max number of produced entities present in the playground at any given time.
            total_production_limit: total number of entities that can be produced.
            entity_produced_params: Dictionary of parameters of the entity produced.
            allow_overlapping: allow overlapping for spawned entities.
            **kwargs:
        """

        Entity.__init__(**kwargs)

        self._production_area = production_area

        self._type_entity_produced = entity_produced
        if not entity_produced_params:
            entity_produced_params = {}
        self._entity_produced_params = entity_produced_params

        self._limit_in_playground = limit_entities_in_playground
        self._total_production_limit = total_production_limit
        self._allow_overlapping = allow_overlapping

        self._total_produced = 0
        self.produced_entities: List[Entity] = []

    def _limit_reached(self):

        return (len(self.produced_entities) < self._limit_in_playground
                and self._total_produced < self._total_production_limit)

    @abstractmethod
    def _is_producing(self):
        ...

    def produce(self):

        if self._is_producing() and not self._limit_reached():

            new_entity: Entity = self._type_entity_produced(temporary=True, **self._entity_produced_params)

            new_entity.produced_by = self

            self._total_produced += 1
            self.produced_entities.append(new_entity)

            initial_position = self._production_area.sample()

            self._playground.add(new_entity,
                                 initial_position=initial_position,
                                 allow_overlapping=self._allow_overlapping)

    def reset(self):
        """
        Reset the spawner by resetting the total count of elements produced.
        """

        self.produced_entities = []
        self._total_produced = 0
