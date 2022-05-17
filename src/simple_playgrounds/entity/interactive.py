from __future__ import annotations
from typing import TYPE_CHECKING

from abc import ABC, abstractmethod

import pymunk

from simple_playgrounds.common.definitions import DEFAULT_INTERACTION_RANGE, INVISIBLE_ALPHA
from simple_playgrounds.entity.embodied import EmbodiedEntity

if TYPE_CHECKING:
    from simple_playgrounds.entity.physical import PhysicalEntity


class InteractiveEntity(EmbodiedEntity, ABC):

    def __init__(self, playground, initial_coordinates, **kwargs):

        super().__init__(playground, initial_coordinates, **kwargs)

        self._activated = False
 
        for pm_shape in self._pm_shapes:
            pm_shape.sensor = True
            # pm_shape.filter = pymunk.ShapeFilter(
            #     categories=2 ** PymunkCollisionCategories.INTERACTION.value,
                # mask=2 ** PymunkCollisionCategories.INTERACTION.value)


        # self._base_sprite.alpha = INVISIBLE_ALPHA

    def get_sprite(self, zoom: float = 1) :
        sprite = super().get_sprite(zoom)
        sprite.alpha = INVISIBLE_ALPHA

        return sprite

    @property
    def activated(self):
        return self._activated

    def pre_step(self):
        self._activated = False

    def post_step(self):
        pass
        
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
        for pm_shape in self._pm_shapes:
            self._playground.space.add(pm_shape)

    def _remove_from_pymunk_space(self):
        for pm_shape in self._pm_shapes:
            self._playground.space.remove(pm_shape)
