""" Module that defines the base class Part and Actuator.

Part inherits from Entity, and is used to create different body parts
of an agent. Parts are visible and movable by default.

Examples on how to add Parts to an agent can be found
in simple_playgrounds/agents/agents.py
"""
from __future__ import annotations
from abc import ABC, abstractmethod
from typing import Dict, List, Optional, TYPE_CHECKING, Tuple, Union

import pymunk
import math

from simple_playgrounds.agent.part.controller import (
    Command,
    Controller,
)
from simple_playgrounds.common.definitions import (
    CollisionTypes,
)
from simple_playgrounds.common.position_utils import InitCoord
from simple_playgrounds.entity.interactive import AnchoredInteractive
from simple_playgrounds.entity.physical import PhysicalEntity

if TYPE_CHECKING:
    from simple_playgrounds.agent.agent import Agent
    from simple_playgrounds.common.position_utils import (
        Coordinate,
    )


CommandDict = Dict[Command, Union[float, int]]


class PhysicalPart(PhysicalEntity, ABC):
    def __init__(self, agent: Agent, **kwargs):

        self._agent = agent
        self._anchored_parts: List[AnchoredPart] = []

        super().__init__(
            **kwargs,
        )

        # Add physical motors if needed
        self._controllers: List[Controller] = self._set_controllers(**kwargs)

        self._agent.add_part(self)
        self._teams = agent.teams

    @property
    def anchored(self):
        return self._anchored_parts

    def add_anchored(self, anchored: AnchoredPart):
        self._anchored_parts.append(anchored)

    def add_interactive(self, interactive: InteractivePart):
        self._interactives.append(interactive)

    def move_to(self, coordinates: Coordinate, keep_velocity: bool = True, **kwargs):

        position, angle = coordinates

        # If joint config are not kept, move base then parts are moved according to anchor position.
        if not keep_velocity:

            super().move_to(
                coordinates=coordinates, keep_velocity=keep_velocity, **kwargs
            )
            for part in self._anchored_parts:
                part_coord = part.get_init_coordinates()
                part.move_to(
                    coordinates=part_coord, keep_velocity=keep_velocity, **kwargs
                )

        # Else, we move first the anchored part then the base.
        else:
            for part in self._anchored_parts:
                new_angle = angle + part.relative_angle
                new_position = position + part.relative_position.rotated(angle)
                part.move_to(
                    coordinates=(new_position, new_angle),
                    keep_velocity=keep_velocity,
                    **kwargs,
                )

            super().move_to(
                coordinates=coordinates, keep_velocity=keep_velocity, **kwargs
            )

    @property
    def _collision_type(self):
        return CollisionTypes.PART

    @abstractmethod
    def _set_controllers(self, **kwargs) -> List[Controller]:
        ...

    @abstractmethod
    def apply_commands(self, **kwargs):
        ...

    @property
    def agent(self):
        return self._agent

    # @property
    # def name(self):
    # return self._name

    @property
    def global_name(self):
        return self._agent.name + "_" + self._name

    @property
    def controllers(self):
        return self._controllers

    # def remove(self, definitive: bool):
    # self._playground.space.remove(self._motor, self._joint, self._limit)
    # for part in self._anchored_parts:
    #     part.remove(definitive)

    # super().remove(definitive=definitive)

    def reset(self):
        super().reset()

        for part in self._anchored_parts:
            part.reset()

        # if self._removed:
        #     self._add_to_pymunk_space()
        # self._playground.space.add(self._joint, self._limit, self._motor)


class Platform(PhysicalPart):
    pass


class AnchoredPart(PhysicalPart, ABC):
    def __init__(
        self,
        anchor: PhysicalPart,
        position_on_anchor: Union[Tuple[float, float], pymunk.Vec2d],
        relative_angle: float,
        rotation_range: float,
        position_on_part: Optional[Union[Tuple[float, float], pymunk.Vec2d]] = None,
        **kwargs,
    ):

        self._anchor = anchor

        if anchor.playground:
            raise ValueError("Parts must be added before addingto playground")

        super().__init__(
            agent=anchor.agent,
            teams=anchor.agent.teams,
            **kwargs,
        )

        self._anchor_point = pymunk.Vec2d(*position_on_anchor)
        if not position_on_part:
            position_on_part = self.default_position_on_part
        self._part_point = pymunk.Vec2d(*position_on_part)
        self._angle_offset = relative_angle

        self._rotation_range = rotation_range

        self._anchor.add_anchored(self)
        self._motor = None
        self._joint = None
        self._limit = None

    @property
    def relative_position(self):
        return (self.position - self._anchor.position).rotated(-self._anchor.angle)

    @property
    def relative_angle(self):
        rel_angle = (self.angle - self._anchor.angle) % (2 * math.pi)

        if rel_angle > math.pi:
            return rel_angle - 2 * math.pi
        return rel_angle

    def get_init_coordinates(self):
        """
        Calculates the position of a Part relative to its Anchor.
        Sets the position of the Part.
        """

        position = (
            self._anchor.position
            + self._anchor_point.rotated(self._anchor.angle)
            - self._part_point.rotated(self._anchor.angle + self._angle_offset)
        )

        angle = self._anchor.pm_body.angle + self._angle_offset

        return position, angle

    def attach_to_anchor(self):

        assert self._playground

        # Create joint to attach to anchor
        self._joint = pymunk.PivotJoint(
            self._anchor.pm_body, self.pm_body, self._anchor_point, self._part_point
        )
        self._joint.collide_bodies = False
        self._limit = pymunk.RotaryLimitJoint(
            self._anchor.pm_body,
            self._pm_body,
            self._angle_offset - self._rotation_range / 2,
            self._angle_offset + self._rotation_range / 2,
        )

        self._motor = pymunk.SimpleMotor(self._anchor.pm_body, self.pm_body, 0)

    @property
    def pm_joints(self):
        assert self._joint and self._limit and self._motor
        return self._joint, self._limit, self._motor

    @property
    @abstractmethod
    def default_position_on_part(self) -> Tuple[float, float]:
        ...


class InteractivePart(AnchoredInteractive):
    def __init__(self, anchor: PhysicalPart, **kwargs):

        self._agent = anchor.agent
        self._controllers: List[Controller] = self._set_controllers(**kwargs)
        super().__init__(anchor=anchor, **kwargs)

        self._agent.add_part(self)
        self._teams = self._agent.teams

    def relative_position(self):

        return (self.position - self._anchor.position).rotated(-self._anchor.angle)

    def relative_angle(self):

        return self.angle - self._anchor.angle

    @abstractmethod
    def _set_controllers(self, **kwargs) -> List[Controller]:
        ...

    @abstractmethod
    def apply_commands(self, **kwargs):
        ...

    @property
    def agent(self):
        return self._agent

    @property
    def global_name(self):
        return self._agent.name + "_" + self._name

    @property
    def controllers(self):
        return self._controllers
