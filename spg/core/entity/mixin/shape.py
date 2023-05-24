from __future__ import annotations

from typing import TYPE_CHECKING, List, Optional, Union

import arcade
import pymunk
from pymunk import autogeometry

if TYPE_CHECKING:
    from spg.core.entity import Entity

Teams = Union[str, List[str]]


class ShapeMixin:
    """
    Mixin for entities with shapes.
    """

    sprite: arcade.Sprite
    scale: float
    radius: float
    pm_body: pymunk.Body
    collision_type: int
    attached: List[Entity]

    def __init__(
        self,
        traversable: bool = False,
        shape_approximation: Optional[str] = None,
        **_,
    ):
        """

        Args:
            traversable: bool, if True, the entity can't be observed and has no physical collisions
            shape_approximation:
            **_:
        """

        self.traversable = traversable
        self.pm_shapes = self._get_pm_shapes(shape_approximation)

        self._set_pm_collision_type()

    def _get_pm_shapes(self, shape_approximation):

        vertices = self.sprite.get_hit_box()

        vertices = [(x * self.scale, y * self.scale) for x, y in vertices]

        if shape_approximation == "circle":
            pm_shapes = [pymunk.Circle(self.pm_body, self.radius)]

        elif shape_approximation == "box":
            top = max(vert[0] for vert in vertices)
            bottom = min(vert[0] for vert in vertices)
            left = min(vert[1] for vert in vertices)
            right = max(vert[1] for vert in vertices)

            box_vertices = ((top, left), (top, right), (bottom, right), (bottom, left))

            pm_shapes = [pymunk.Poly(self.pm_body, box_vertices)]

        elif shape_approximation == "hull":
            pm_shapes = [pymunk.Poly(self.pm_body, vertices)]

        elif shape_approximation == "decomposition":

            if not autogeometry.is_closed(vertices):
                vertices += [vertices[0]]

            if pymunk.area_for_poly(vertices) < 0:
                vertices = list(reversed(vertices))

            list_vertices = autogeometry.convex_decomposition(vertices, tolerance=0.5)

            pm_shapes = []
            for vertices in list_vertices:
                pm_shape = pymunk.Poly(body=self.pm_body, vertices=vertices)
                pm_shapes.append(pm_shape)

        else:
            pm_shapes = [pymunk.Poly(body=self.pm_body, vertices=vertices)]

        for pm_shape in pm_shapes:
            pm_shape.friction = FRICTION_ENTITY
            pm_shape.elasticity = ELASTICITY_ENTITY
            pm_shape.filter = pymunk.ShapeFilter(categories=1, mask=1)

        if self.traversable:
            for pm_shape in pm_shapes:
                pm_shape.sensor = True

        return pm_shapes

    def _set_pm_collision_type(self):

        if not hasattr(self, "collision_type"):
            return

        for pm_shape in self.pm_shapes:
            pm_shape.collision_type = self.collision_type

    def get_dummy_shapes(self, body):

        dummy_shapes = []
        for pm_shape in self.pm_shapes:
            dummy_shape = pm_shape.copy()
            dummy_shape.body = body
            dummy_shape.sensor = True
            dummy_shapes.append(dummy_shape)

        for entity in self.attached:
            dummy_shapes += entity.get_dummy_shapes(body)

        return dummy_shapes

    def get_all_shapes(self):
        all_shapes = self.pm_shapes
        for entity in self.attached:
            all_shapes += entity.get_all_shapes()
        return all_shapes


FRICTION_ENTITY = 0.8
ELASTICITY_ENTITY = 0.5
