from __future__ import annotations

from abc import abstractmethod
from typing import TYPE_CHECKING, List, Union

import pymunk

if TYPE_CHECKING:
    from spg.entity import Entity, Agent
    from spg.playground import Playground

from spg.playground.collision import CollisionTypes


class ActivableMixin:

    activated = False
    collision_type = CollisionTypes.ACTIVABLE
    teams: List[str]

    @abstractmethod
    def activate(self, entity, **kwargs):
        ...


class ActionMixin:
    @property
    @abstractmethod
    def action_space(self):
        ...

    @abstractmethod
    def apply_action(self, action):
        ...


class ObservationMixin:
    @property
    @abstractmethod
    def observation_space(self):
        ...

    @abstractmethod
    def get_observation(self):
        ...


class BarrierMixin:

    blocked: List[Entity] = []
    index_barrier: int
    pm_shapes: List[pymunk.Shape]
    _playground: Playground

    @property
    def playground(self):
        return self._playground

    @playground.setter
    def playground(self, playground):

        self._playground = playground
        self.playground.barriers.append(self)
        self.index_barrier = len(self.playground.barriers)

        categories = 2**self.index_barrier
        mask = 1 | 2**self.index_barrier

        for pm_shape in self.pm_shapes:
            pm_shape.filter = pymunk.ShapeFilter(categories=categories, mask=mask)

    def block(self, *entities: Union[Agent, Entity]):

        for entity in entities:
            self.blocked.append(entity)
            self._block(entity)

            for attached in entity.attached:
                self.block(attached)

    def _block(self, entity):

        if not hasattr(self, 'index_barrier'):
            raise AttributeError('playground not set')

        for pm_shape in entity.pm_shapes:
            categories = pm_shape.filter.categories | 2**self.index_barrier
            mask = pm_shape.filter.mask | 2**self.index_barrier
            pm_shape.filter = pymunk.ShapeFilter(categories=categories, mask=mask)

