from __future__ import annotations

from abc import ABC
from typing import TYPE_CHECKING, Dict, List, Optional, Tuple, Union

import pymunk

from spg.definitions import CollisionTypes
from spg.position import Coordinate
from .mixin import (
    ActionMixin,
    AttachedStaticMixin,
    BaseMixin,
    ObservationMixin,
    ShapeMixin,
    SpriteMixin,
)
from .mixin.body import BodyMixin

if TYPE_CHECKING:
    from ..playground import Playground

Teams = Union[str, List[str]]


class Entity(SpriteMixin, BodyMixin, ShapeMixin, ABC):
    """
    Entities are elementary entities physically present in the playground.

    """

    _playground: Playground
    pm_body: pymunk.Body
    pm_shapes: List[pymunk.Shape]

    def __init__(
        self,
        name: Optional[str] = None,
        teams: Optional[Teams] = None,
        **kwargs,
    ):

        self.name = name

        # Teams
        if isinstance(teams, str):
            teams = [teams]
        elif not teams:
            teams = []
        self.teams = teams

        SpriteMixin.__init__(self, **kwargs)
        BodyMixin.__init__(self, **kwargs)
        ShapeMixin.__init__(self, **kwargs)

        self.attached: List[Entity] = []
        self.attachment_points: Dict[Entity, Coordinate] = {}
        self.anchor: Optional[Entity] = None

    def pre_step(self):
        """
        Preliminary calculations before the pymunk engine steps.
        """
        self._moved = False
        pass

    def post_step(self):
        """
        Updates the entity state after pymunk engine steps.
        """
        pass

    def add(
        self,
        attached_entity: Entity,
        anchor_attachment_point: Tuple[float, float] = (0, 0),
        relative_angle: float = 0,
    ):

        """
        Attach an entity to the current entity.
        """

        self.attached.append(attached_entity)
        self.attachment_points[attached_entity] = (
            anchor_attachment_point,
            relative_angle,
        )
        attached_entity.anchor = self
        attached_entity.teams = self.teams

        if isinstance(attached_entity, AttachedStaticMixin):
            for shape in attached_entity.pm_shapes:
                shape.body = self.pm_body


class Element(Entity, BaseMixin):
    pass


class Agent(Entity, BaseMixin, ActionMixin, ObservationMixin):

    reward = 0
    cumulative_reward = 0
    collision_type = CollisionTypes.AGENT

    def pre_step(self):
        super().pre_step()
        self.reward = 0

    def post_step(self):
        super().post_step()
        self.cumulative_reward += self.reward
