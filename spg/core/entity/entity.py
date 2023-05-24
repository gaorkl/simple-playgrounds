from __future__ import annotations

from abc import ABC
from typing import TYPE_CHECKING, Dict, List, Optional, Tuple, Union

import pymunk
from gymnasium import spaces

from spg.core.collision import CollisionTypes
from spg.core.position import Coordinate
from .action import ActionMixin
from .mixin import (
    AttachedStaticMixin,
    BaseMixin,
    ShapeMixin,
    SpriteMixin,
)
from .mixin.body import BodyMixin
from .sensor import SensorMixin
from ..sensor.ray.ray import RaySensor

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

    @property
    def all_attached(self):
        """
        Returns all entities attached to the agents.
        """
        attached = self.attached.copy()
        for entity in self.attached:
            attached.extend(entity.all_attached)
        return attached

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

        if isinstance(attached_entity, RaySensor):
            attached_entity.add_invisible_entity(self)


class Element(Entity, BaseMixin):
    pass


class Agent(Entity, BaseMixin, ActionMixin, SensorMixin):

    reward = 0
    cumulative_reward = 0
    collision_type = CollisionTypes.AGENT

    def pre_step(self):
        super().pre_step()
        self.reward = 0

    def post_step(self):
        super().post_step()
        self.cumulative_reward += self.reward

    @property
    def agent_action_space(self):

        act_space = {self.name: self.action_space}

        # Add attached entities' action spaces
        for attached in self.all_attached:
            if hasattr(attached, "action_space"):
                act_space[attached.name] = attached.action_space

        return spaces.Dict(act_space)

    def agent_apply_action(self, action):

        self.apply_action(action[self.name])

        # Apply attached entities' actions
        for attached in self.all_attached:
            if hasattr(attached, "apply_action"):
                attached.apply_action(action[attached.name])

    @property
    def agent_observation_space(self):

        obs_space = {self.name: self.observation_space}

        # Add attached entities' observation spaces
        for attached in self.all_attached:
            if hasattr(attached, "observation_space"):
                obs_space[attached.name] = attached.observation_space

        return spaces.Dict(obs_space)

    @property
    def agent_observation(self):

        obs = {self.name: self.observation}

        # Add attached entities' observations
        for attached in self.all_attached:
            if hasattr(attached, "observation"):
                obs[attached.name] = attached.observation

        return obs
