from __future__ import annotations
from typing import TYPE_CHECKING, List

from abc import ABC, abstractmethod

import pymunk

from simple_playgrounds.common.definitions import (
    DEFAULT_INTERACTION_RANGE,
    INVISIBLE_ALPHA,
    CollisionTypes,
)
from simple_playgrounds.entity.embodied import EmbodiedEntity

if TYPE_CHECKING:
    from simple_playgrounds.entity.physical import PhysicalEntity


class InteractiveEntity(EmbodiedEntity, ABC):
    def __init__(self, **kwargs):

        super().__init__(**kwargs)

        for pm_shape in self._pm_shapes:
            pm_shape.sensor = True
            # pm_shape.filter = pymunk.ShapeFilter(
            #     categories=2 ** PymunkCollisionCategories.INTERACTION.value,
            # mask=2 ** PymunkCollisionCategories.INTERACTION.value)

        # self._base_sprite.alpha = INVISIBLE_ALPHA

    def get_sprite(self, zoom: float = 1):
        sprite = super().get_sprite(zoom)
        sprite.alpha = INVISIBLE_ALPHA

        return sprite

    def update_team_filter(self):

        if not self._teams:
            return

        # categ = 2 ** PymunkCollisionCategories.INTERACTION.value
        # mask= 2 ** PymunkCollisionCategories.INTERACTION.value

        categ = 0
        # categ = 2 ** PymunkCollisionCategories.INTERACTION.value
        for team in self._teams:
            categ = categ | 2 ** self._playground.teams[team]

        mask = 0
        for team in self._playground.teams:

            mask = mask | 2 ** self._playground.teams[team]
            if team not in self._teams:
                mask = mask ^ 2 ** self._playground.teams[team]

        for pm_shape in self._pm_shapes:
            pm_shape.filter = pymunk.ShapeFilter(categories=categ, mask=mask)


class StandAloneInteractive(InteractiveEntity, ABC):
    def _get_pm_body(self):
        return pymunk.Body(body_type=pymunk.Body.STATIC)


class AnchoredInteractive(InteractiveEntity, ABC):
    def __init__(
        self,
        anchor: PhysicalEntity,
        interaction_range: float = DEFAULT_INTERACTION_RANGE,
        **kwargs,
    ):

        self._anchor = anchor

        if anchor.playground:
            raise ValueError("Interactives must be added before adding to playground")

        radius = self._anchor.radius + interaction_range
        texture = self._anchor.texture

        super().__init__(
            texture=texture,
            radius=radius,
            teams=self._anchor._teams,
            **kwargs,
        )

        self._anchor.add_interactive(self)

    @property
    def anchor(self):
        return self._anchor

    def _get_pm_body(self):
        return self._anchor._pm_body

    @property
    def pm_elements(self):
        return self._pm_shapes


class Graspable(AnchoredInteractive):
    def __init__(
        self,
        anchor: PhysicalEntity,
        interaction_range: float = DEFAULT_INTERACTION_RANGE,
        **kwargs,
    ):
        super().__init__(anchor, interaction_range, **kwargs)

        self.grasped_by: List[EmbodiedEntity] = []

    @property
    def _collision_type(self):
        return CollisionTypes.GRASPABLE
