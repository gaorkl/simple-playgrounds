from __future__ import annotations

from abc import ABC
from typing import Optional

import pymunk

from ..utils.definitions import PymunkCollisionCategories
from .embodied import EmbodiedEntity


class PhysicalEntity(EmbodiedEntity, ABC):
    """
    PhysicalEntity creates a physical object that can collide with
    other Physical Entities.
    It deals with physical properties such as the mass, visual texture,
     whether it is transparent or traversable.
    PhysicalEntity is visible and non-traversable by default.
    An agent is composed of multiple PhysicalEntity that are attached to each other.
    """

    def __init__(
        self,
        mass: Optional[float] = None,
        traversable: bool = False,
        transparent: bool = False,
        **kwargs,
    ):

        self._mass = mass
        self._transparent = transparent
        self._traversable = traversable

        super().__init__(**kwargs)

        self._set_shape_collision_filter()

    @property
    def transparent(self):
        return self._transparent

    @property
    def traversable(self):
        return self._traversable

    @property
    def movable(self):
        return bool(self._mass)

    @property
    def needs_sprite_update(self):
        return self._moved or self.movable

    ########################
    # BODY AND SHAPE
    ########################

    def _get_pm_body(self):

        if not self._mass:
            return pymunk.Body(body_type=pymunk.Body.STATIC)

        vertices = self._base_sprite.get_hit_box()
        moment = pymunk.moment_for_poly(self._mass, vertices)

        return pymunk.Body(self._mass, moment, body_type=pymunk.Body.DYNAMIC)

    def _set_shape_collision_filter(self):

        # By default, a physical entity collides with all
        if self._transparent and self._traversable:
            raise ValueError(
                "Physical Entity can not be transparent and traversable.\
                Use Interactive Entity."
            )

        categories = 2**PymunkCollisionCategories.NO_TEAM.value
        mask = (
            pymunk.ShapeFilter.ALL_MASKS()
            ^ 2**PymunkCollisionCategories.TRAVERSABLE.value
        )

        # If traversable, collides with nothing
        if self._traversable:
            categories = 2**PymunkCollisionCategories.TRAVERSABLE.value
            mask = 0

        # If transparent, collides with everything except tra.
        # if self._transparent:
        #     categories = 2 ** PymunkCollisionCategories.TRANSPARENT.value

        for pm_shape in self._pm_shapes:
            pm_shape.filter = pymunk.ShapeFilter(categories=categories, mask=mask)
