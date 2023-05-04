from __future__ import annotations

from typing import TYPE_CHECKING

import pymunk

from spg.definitions import PYMUNK_STEPS, CollisionTypes
from ...entity.mixin import ActivableMixin

if TYPE_CHECKING:
    from ...entity import Entity
    from ..playground import Playground


SIMULATION_STEPS = 10
SPACE_DAMPING = 0.9


class SpaceManager:

    space: pymunk.Space

    def __init__(self, pymunk_steps=PYMUNK_STEPS, **kwargs):
        assert pymunk_steps > 0
        self.pymunk_steps = pymunk_steps

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

    def add_interactions(self):

        self._add_handler(
            CollisionTypes.AGENT, CollisionTypes.ACTIVABLE, agent_activable_interaction
        )

        self._add_handler(
            CollisionTypes.TRIGGER,
            CollisionTypes.ACTIVABLE,
            trigger_activable_interaction,
        )

        self._add_handler(
            CollisionTypes.ACTIVABLE,
            CollisionTypes.ACTIVABLE,
            activable_activable_interaction,
        )

    def _add_handler(
        self,
        collision_type_1: CollisionTypes,
        collision_type_2: CollisionTypes,
        interaction_function,
    ):
        handler = self.space.add_collision_handler(collision_type_1, collision_type_2)
        handler.pre_solve = interaction_function
        handler.data["playground"] = self


def get_colliding_entities(playground: Playground, arbiter):

    entity_1 = playground.shapes_to_entities[arbiter.shapes[0]]
    entity_2 = playground.shapes_to_entities[arbiter.shapes[1]]

    return entity_1, entity_2


def agent_activable_interaction(arbiter, space, data):

    agent_part, activable = get_colliding_entities(data["playground"], arbiter)
    assert isinstance(activable, ActivableMixin)

    # if intersection of teams is not empty, then agent is allowed to activate
    if not set(activable.teams).intersection(set(agent_part.teams)):
        if activable.teams and agent_part.teams:
            return True

    activable.activate(agent_part)

    return True


def trigger_activable_interaction(arbiter, space, data):

    element_part, activable = get_colliding_entities(data["playground"], arbiter)
    assert isinstance(activable, ActivableMixin)

    if not set(activable.teams).intersection(set(element_part.teams)):
        if activable.teams and element_part.teams:
            return True

    activable.activate(element_part)

    return True


def activable_activable_interaction(arbiter, space, data):

    activable_1, activable_2 = get_colliding_entities(data["playground"], arbiter)
    assert isinstance(activable_1, ActivableMixin)
    assert isinstance(activable_2, ActivableMixin)

    if not set(activable_1.teams).intersection(set(activable_2.teams)):
        if activable_1.teams and activable_2.teams:
            return True

    activable_1.activate(activable_2)
    activable_2.activate(activable_1)

    return True





