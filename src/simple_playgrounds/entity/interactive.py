from abc import ABC, abstractmethod

import pymunk

from simple_playgrounds.common.contour import expand_contour
from simple_playgrounds.common.definitions import PymunkCollisionCategories, INVISIBLE_ALPHA, DEFAULT_INTERACTION_RANGE
from simple_playgrounds.entity.entity import EmbodiedEntity
from simple_playgrounds.entity.physical import PhysicalEntity


class InteractiveEntity(EmbodiedEntity, ABC):

    def __init__(self, **kwargs):

        super().__init__(**kwargs)

        self._set_pm_collision_type()

    def _set_pm_shape(self):
        self._pm_interactive_shape = self._create_pm_shape()
        self._pm_interactive_shape.sensor = True

        self._pm_interactive_shape.filter = pymunk.ShapeFilter(
            categories=2 ** PymunkCollisionCategories.INTERACTION.value,
            mask=2 ** PymunkCollisionCategories.INTERACTION.value)

    @abstractmethod
    def _set_pm_collision_type(self):
        """
        Set the collision handler for the interactive shape.
        """
        ...

    def draw(self, surface, viewpoint, draw_transparent=False):

        if not draw_transparent:
            return

        mask = self._create_mask(alpha=INVISIBLE_ALPHA)
        mask_rect = mask.get_rect()
        mask_rect.center = self.position - viewpoint
        surface.blit(mask, mask_rect, None)

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

        self._pm_interactive_shape.filter = pymunk.ShapeFilter(categories=categ, mask=mask)


class StandAloneInteractive(InteractiveEntity, ABC):

    def _set_pm_body(self):
        return pymunk.Body(body_type=pymunk.Body.STATIC)

    def _add_to_playground(self, **kwargs):
        self._playground.space.add(self._pm_body, self._pm_interactive_shape)

        self._set_initial_coordinates(**kwargs)
        self._move_to_initial_position()

        self._playground.shapes_to_entities[self._pm_interactive_shape] = self
        self._playground.entities.append(self)

    def _remove_from_playground(self):
        self._playground.space.remove(self._pm_body, self._pm_interactive_shape)
        self._playground.shapes_to_entities.pop(self._pm_interactive_shape)
        self._playground.entities.remove(self)


class AnchoredInteractive(InteractiveEntity, ABC):

    def __init__(self,
                 anchor: PhysicalEntity,
                 interaction_range: float = DEFAULT_INTERACTION_RANGE,
                 **kwargs):

        self._anchor = anchor
        anchor_contour = anchor.contour
        interaction_contour = expand_contour(anchor_contour, interaction_range)

        kwargs = {**interaction_contour._asdict(), **kwargs}

        super().__init__(**kwargs)

    def _set_pm_body(self):
        return self._anchor._pm_body

    def _add_to_playground(self):
        self._playground.space.add(self._pm_interactive_shape)
        self._playground.shapes_to_entities[self._pm_interactive_shape] = self

    def _remove_from_playground(self):
        self._playground.space.remove(self._pm_interactive_shape)
        self._playground.shapes_to_entities.pop(self._pm_interactive_shape)