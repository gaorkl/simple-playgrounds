from __future__ import annotations

from typing import List, Union

import pymunk

from spg.core.entity import Entity, Agent
from spg.core.playground import Playground


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

        if not hasattr(self, "index_barrier"):
            raise AttributeError("playground not set")

        for pm_shape in entity.pm_shapes:
            categories = pm_shape.filter.categories | 2**self.index_barrier
            mask = pm_shape.filter.mask | 2**self.index_barrier
            pm_shape.filter = pymunk.ShapeFilter(categories=categories, mask=mask)
