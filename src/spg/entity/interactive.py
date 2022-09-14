from __future__ import annotations

from abc import ABC
from typing import TYPE_CHECKING, List, Optional

import pymunk

from ..utils.definitions import (
    DEFAULT_INTERACTION_RANGE,
    INVISIBLE_ALPHA,
    CollisionTypes,
)
from .embodied import EmbodiedEntity

if TYPE_CHECKING:
    from spg.entity.physical import PhysicalEntity


class InteractiveEntity(EmbodiedEntity, ABC):
    def __init__(self, **kwargs):

        super().__init__(**kwargs)

        for pm_shape in self._pm_shapes:
            pm_shape.sensor = True
            # pm_shape.filter = pymunk.ShapeFilter(
            #     categories=2 ** PymunkCollisionCategories.INTERACTION.value,
            # mask=2 ** PymunkCollisionCategories.INTERACTION.value)

        # self._base_sprite.alpha = INVISIBLE_ALPHA

    def get_sprite(self, zoom: float = 1, color_uid=None):
        sprite = super().get_sprite(zoom, color_uid)
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


class InteractiveZone(InteractiveEntity, ABC):
    def _get_pm_body(self):
        return pymunk.Body(body_type=pymunk.Body.STATIC)


class InteractiveAnchored(InteractiveZone, ABC):
    def __init__(
        self,
        anchor: Optional[PhysicalEntity] = None,
        interaction_range: float = DEFAULT_INTERACTION_RANGE,
        **kwargs,
    ):

        if anchor:
            texture = anchor.texture
            radius = anchor.radius + interaction_range
            super().__init__(texture=texture, radius=radius, **kwargs)

        else:
            super().__init__(**kwargs)

        self._anchor = None

    @property
    def pm_body(self):
        return self._pm_body

    @pm_body.setter
    def pm_body(self, pm_body):
        self._pm_body = pm_body

        for pm_shape in self._pm_shapes:
            pm_shape.body = self._pm_body

    @property
    def teams(self):
        return self._teams

    @teams.setter
    def teams(self, teams):
        self._teams = teams

    @property
    def anchor(self):
        return self._anchor

    @anchor.setter
    def anchor(self, anchor: PhysicalEntity):
        self._anchor = anchor

        for pm_shape in self._pm_shapes:
            pm_shape.body = self._anchor.pm_body

        self._pm_body = self._anchor.pm_body

    def _get_pm_body(self):
        return None

    @property
    def pm_elements(self):
        return self._pm_shapes

    @property
    def needs_sprite_update(self):
        assert self._anchor
        return self._anchor.needs_sprite_update


class Graspable(InteractiveAnchored):
    def __init__(
        self,
        **kwargs,
    ):
        super().__init__(**kwargs)

        self.grasped_by: List[EmbodiedEntity] = []

    @property
    def _collision_type(self):
        return CollisionTypes.GRASPABLE
