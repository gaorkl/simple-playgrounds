from __future__ import annotations
from abc import ABC
from typing import Optional, List, TYPE_CHECKING
if TYPE_CHECKING:
    from simple_playgrounds.entity.interactive import InteractiveEntity

import pymunk

from simple_playgrounds.agent.actuators import Grasp
from simple_playgrounds.common.contour import GeometricShapes
from simple_playgrounds.common.definitions import PymunkCollisionCategories, INVISIBLE_ALPHA, \
    VISIBLE_ALPHA

from simple_playgrounds.entity.entity import EmbodiedEntity


class PhysicalEntity(EmbodiedEntity, ABC):
    """
    PhysicalEntity creates a physical object that can collide with other Physical Entities.
    It deals with physical properties such as the mass, visual texture, whether it is transparent or traversable.
    PhysicalEntity is visible and non-traversable by default.
    An agent is composed of multiple PhysicalEntity that are attached to each other.
    """

    def __init__(
            self,
            movable: bool = False,
            mass: Optional[float] = None,
            traversable: bool = False,
            transparent: bool = False,
            **kwargs,
    ):

        if movable:
            assert mass
        self._movable = movable

        self._mass = mass

        super().__init__(**kwargs)

        self._transparent = transparent
        self._traversable = traversable
        self._set_shape_collision_filter()

        self._held_by: List[Grasp] = []
        self._interactives: List[InteractiveEntity] = []

    @property
    def held_by(self):
        return self._held_by

    @held_by.setter
    def held_by(self, grasper: Grasp):
        self._held_by.append(grasper)

    def released_by(self, grasper):
        assert grasper in self._held_by
        self._held_by.remove(grasper)

    @property
    def movable(self):
        return self._movable

    # BODY AND SHAPE
    def _set_pm_body(self):

        if not self._movable:
            return pymunk.Body(body_type=pymunk.Body.STATIC)

        assert isinstance(self._mass, (float, int))

        if self._contour.shape == GeometricShapes.CIRCLE:
            moment = pymunk.moment_for_circle(self._mass, 0,
                                              self._contour.radius)

        else:
            moment = pymunk.moment_for_poly(self._mass, self._contour.vertices)

        return pymunk.Body(self._mass, moment)

    def _set_pm_shape(self):
        return self._create_pm_shape()

    def _set_shape_debug_color(self):
        self._pm_shape.color = tuple(list(self.base_color) + [VISIBLE_ALPHA])

    def _add_pm_elements(self, **kwargs):
        self._playground.space.add(self._pm_body, self._pm_shape)
        self._playground._shapes_to_entities[self._pm_shape] = self

        self._set_initial_coordinates(**kwargs)
        self._move_to_initial_position()

        for interactive in self._interactives:
            interactive.add_to_playground(self._playground)

    def _remove_pm_elements(self):
        self._playground.space.remove(self._pm_body, self._pm_shape)
        self._playground._shapes_to_entities.pop(self._pm_shape)

        for interactive in self._interactives:
            interactive.remove_from_playground()

    def _set_shape_collision_filter(self):

        # By default, a physical entity collides with all
        if self._transparent and self._traversable:
            raise ValueError('Physical Object can not be transparent and traversable')

        self._pm_shape.filter = pymunk.ShapeFilter(categories=2 ** PymunkCollisionCategories.DEFAULT.value,
                                                   mask=pymunk.ShapeFilter.ALL_MASKS() ^
                                                   2 ** PymunkCollisionCategories.TRAVERSABLE.value)

        # If traversable, collides only with sensors
        if self._traversable:
            self._pm_shape.filter = pymunk.ShapeFilter(categories=2 ** PymunkCollisionCategories.TRAVERSABLE.value,
                                                       mask=2 ** PymunkCollisionCategories.SENSOR.value |
                                                       2 ** PymunkCollisionCategories.SENSOR_CONTACT.value)

        # If transparent, collides with everything. Sensors don't collide except for contact sensor.
        if self._transparent:
            self._pm_shape.filter = pymunk.ShapeFilter(categories=2 ** PymunkCollisionCategories.TRANSPARENT.value,
                                                       mask=pymunk.ShapeFilter.ALL_MASKS() ^
                                                       (2 ** PymunkCollisionCategories.SENSOR.value))

    def add_to_team(self, team):
        super().add_to_team(team)

        for interactive in self._interactives:
            interactive.add_to_team(team)

    def update_team_filter(self):

        categ = self._pm_shape.filter.categories
        for team in self._teams:
            categ = categ | 2 ** self._playground.teams[team]

        mask = self._pm_shape.filter.mask
        for team in self._playground.teams:

            if team not in self._teams:
                mask = mask | 2 ** self._playground.teams[team] ^ 2 ** self._playground.teams[team]

        self._pm_shape.filter = pymunk.ShapeFilter(categories=categ, mask=mask)

        for interactive in self._interactives:
            interactive.update_team_filter()

    def add_interactive(self, entity: InteractiveEntity):
        self._interactives.append(entity)

        if not entity.playground and self._playground:
            entity.add_to_playground(self._playground)

        if self._teams:
            entity.add_to_team(self._teams)

    def pre_step(self):
        """
        Performs calculation before the physical environment steps.
        """
        if self._trajectory:
            self.move_to(next(self._trajectory))

    def reset(self):
        """
        Reset the trajectory and initial position
        """
        self._move_to_initial_position()

    def draw(self, surface, viewpoint, draw_transparent=False):

        if self._transparent and not draw_transparent:
            return

        if self._transparent:
            mask = self._create_mask(alpha=INVISIBLE_ALPHA)
        else:
            mask = self._create_mask(alpha=VISIBLE_ALPHA)

        mask_rect = mask.get_rect()
        mask_rect.center = self.position - viewpoint
        surface.blit(mask, mask_rect, None)