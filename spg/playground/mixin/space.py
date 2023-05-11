from __future__ import annotations

from typing import TYPE_CHECKING, Dict

import pymunk

if TYPE_CHECKING:
    from ...entity import Entity

SIMULATION_STEPS = 10
SPACE_DAMPING = 0.9

PYMUNK_STEPS = 10

class SpaceManager:

    space: pymunk.Space

    def __init__(self, pymunk_steps=PYMUNK_STEPS, **kwargs):
        assert pymunk_steps > 0
        self.pymunk_steps = pymunk_steps
        self.custom_collision_types: Dict[str, int] = {}

    def initialize_space(self):
        """Method to initialize Pymunk empty space for 2D physics.

        Returns: Pymunk Space

        """
        self.space = pymunk.Space()
        self.space.gravity = pymunk.Vec2d(0.0, 0.0)
        self.space.damping = SPACE_DAMPING

        self.add_interactions()

    def pymunk_step(self):
        for _ in range(self.pymunk_steps):
            self.space.step(1.0 / self.pymunk_steps)

    def check_overlapping(self, entity: Entity, coordinates: object) -> object:

        entity_shapes = entity.get_all_shapes()

        # Generate dummy shapes to check for overlaps
        dummy_body = pymunk.Body(body_type=pymunk.Body.STATIC)
        dummy_shapes = entity.get_dummy_shapes(dummy_body)

        self.space.add(dummy_body, *dummy_shapes)
        dummy_body.position, dummy_body.angle = coordinates

        self.space.reindex_static()

        overlaps = []
        for dummy_shape in dummy_shapes:
            overlaps += self.space.shape_query(dummy_shape)
        self.space.remove(dummy_body, *dummy_shapes)

        # # remove sensor shapes
        overlaps = [
            elem
            for elem in overlaps
            if elem.shape and not elem.shape.sensor and elem.shape not in entity_shapes
        ]

        return bool(overlaps)
