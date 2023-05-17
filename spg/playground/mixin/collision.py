from __future__ import annotations

from typing import TYPE_CHECKING, Dict

import pymunk

from ...entity.mixin import ActivableMixin
from ..collision import CollisionTypes

if TYPE_CHECKING:
    from ..playground import Playground


SIMULATION_STEPS = 10
SPACE_DAMPING = 0.9

PYMUNK_STEPS = 10


class CollisionManager:

    space: pymunk.Space

    def __init__(self, **kwargs) -> None:
        self.custom_collision_types: Dict[str, int] = {}

    def get_new_collision_type(self, name: str) -> int:

        new_index = max(CollisionTypes) + len(self.custom_collision_types) + 1
        self.custom_collision_types[name] = new_index

        return new_index

    def add_interactions(self):

        self.add_handler(
            CollisionTypes.AGENT, CollisionTypes.ACTIVABLE, agent_activable_interaction
        )

        self.add_handler(
            CollisionTypes.TRIGGER,
            CollisionTypes.ACTIVABLE,
            trigger_activable_interaction,
        )

        self.add_handler(
            CollisionTypes.ACTIVABLE,
            CollisionTypes.ACTIVABLE,
            activable_activable_interaction,
        )

    def add_handler(
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
