from __future__ import annotations
from typing import TYPE_CHECKING

from abc import ABC, abstractmethod

import pymunk

from simple_playgrounds.common.definitions import PymunkCollisionCategories, INVISIBLE_ALPHA, DEFAULT_INTERACTION_RANGE
from simple_playgrounds.entity.embodied.embodied import EmbodiedEntity
from simple_playgrounds.entity.embodied.contour import Contour

if TYPE_CHECKING:
    from simple_playgrounds.entity.embodied.physical import PhysicalEntity
    from simple_playgrounds.common.view import View


class InteractiveEntity(EmbodiedEntity, ABC):

    def __init__(self, **kwargs):

        super().__init__(**kwargs)

        self._activated = False

    @property
    def activated(self):
        return self._activated

    def pre_step(self):
        self._activated = False

    def post_step(self):
        pass

    def _get_pm_shape(self):
        pm_shape = super()._get_pm_shape()
        pm_shape.sensor = True

        pm_shape.filter = pymunk.ShapeFilter(
            categories=2 ** PymunkCollisionCategories.INTERACTION.value,
            mask=2 ** PymunkCollisionCategories.INTERACTION.value)

        return pm_shape

    def update_team_filter(self):

        if not self._teams:
            return

        categ = 0
        for team in self._teams:
            categ = categ | 2 ** self._playground.teams[team]

        mask = 0
        for team in self._playground.teams:

            mask = mask | 2 ** self._playground.teams[team]
            if team not in self._teams:
                mask = mask ^ 2 ** self._playground.teams[team]

        self._pm_shape.filter = pymunk.ShapeFilter(categories=categ, mask=mask)

   
class StandAloneInteractive(InteractiveEntity, ABC):
    
    def _set_pm_body(self):
        return pymunk.Body(body_type=pymunk.Body.STATIC)


class AnchoredInteractive(InteractiveEntity, ABC):

    def __init__(self,
                 anchor: PhysicalEntity,
                 interaction_range: float = DEFAULT_INTERACTION_RANGE,
                 **kwargs):

        self._anchor = anchor
        radius = self._anchor.radius + interaction_range
        texture = self._anchor.texture

        super().__init__(playground=anchor.playground, 
                         initial_coordinates=anchor.coordinates,
                         texture = texture,
                         radius = radius,
                         teams=self._anchor._teams,
                         **kwargs)

        self._anchor.add_interactive(self)

    @property
    def anchor(self):
        return self._anchor

    def _get_pm_body(self):
        return self._anchor._pm_body

    def _add_to_pymunk_space(self):
        self._playground.space.add(self._pm_shape)

    def _remove_from_pymunk_space(self):
        self._playground.space.remove(self._pm_shape)
