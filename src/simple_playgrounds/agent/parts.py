""" Module that defines the base class Part and Actuator.

Part inherits from Entity, and is used to create different body parts
of an agent. Parts are visible and movable by default.

Examples on how to add Parts to an agent can be found
in simple_playgrounds/agents/agents.py
"""
from __future__ import annotations

import math
from abc import ABC
from enum import IntEnum, auto
from typing import Tuple, TYPE_CHECKING, Optional, List
if TYPE_CHECKING:
    from simple_playgrounds.agent.agent import Agent
    from simple_playgrounds.agent.actuators import ActuatorDevice

import pymunk

from simple_playgrounds.common.definitions import ARM_MAX_FORCE, CollisionTypes
from simple_playgrounds.common.entity import Entity
from simple_playgrounds.configs.parser import parse_configuration


# pylint: disable=line-too-long


class Part(Entity, ABC):
    """
    Base class for Body Parts.
    Part inherits from Entity. It is a visible Entity.
    """

    # pylint: disable=too-many-instance-attributes

    def __init__(
        self,
        can_absorb: bool = False,
        movable: bool = True,
        **kwargs,
    ):
        Entity.__init__(self,
                        visible_shape=True,
                        invisible_shape=False,
                        movable=movable,
                        **kwargs)

        self.can_absorb = can_absorb

        self._agent: Optional[Agent] = None

        self._actuators: List[ActuatorDevice] = []

    @property
    def agent(self):
        return self._agent

    @agent.setter
    def agent(self, agent):
        self._agent = agent

    @property      
    def actuators(self):
        return self._actuators

    def add_actuator(self, act):
        self._actuators.append(act)

    def _set_shape_collision(self):
        self.pm_visible_shape.collision_type = CollisionTypes.PART

    def reset(self):
        pass


# Platforms


class Platform(Part, ABC):
    """
    Base class for Platforms.
    Platform can move in space using force actuators that propels them.
    """
    def __init__(
        self,
        can_absorb: bool = False,
        movable: bool = True,
        **kwargs,
    ):
        default_config = parse_configuration('agent_parts', PartTypes.PLATFORM)
        kwargs = {**default_config, **kwargs}

        Part.__init__(self, can_absorb=can_absorb, movable=movable, **kwargs)


class MobilePlatform(Platform):
    """
        Platform that is moving.

    """
    def __init__(self, can_absorb, **kwargs):
        super().__init__(can_absorb=can_absorb, movable=True, **kwargs)


class FixedPlatform(Platform):
    """
        Platform that is fixed.
        Can be used to build Arms with fixed base.
        Refer to the base class Platform.

    """
    def __init__(self, can_absorb, **kwargs):
        super().__init__(can_absorb=can_absorb, movable=False, **kwargs)


# Body parts


class AnchoredPart(Part, ABC):
    """
    Base class for Anchored Parts.

    An Anchored part is attached to an other Part (anchor).
    They are joined at a single point.
    A Part can never collide with its Anchor.
    """

    # pylint: disable=too-many-instance-attributes

    def __init__(
        self,
        anchor: Part,
        position_anchor: Tuple[float, float] = (0, 0),
        position_part: Tuple[float, float] = (0, 0),
        rotation_range: float = math.pi / 4,
        angle_offset: float = 0,
        can_absorb: bool = False,
        movable: bool = True,
        **kwargs,
    ):
        """

        Args:
            anchor:
            position_anchor:
            position_part:
            rotation_range:
            angle_offset:
            can_absorb:
            movable:
            **kwargs:
        """

        Part.__init__(self, can_absorb=can_absorb, movable=movable, **kwargs)

        self.anchor: Part = anchor
        self.angle_offset = angle_offset
        self.rotation_range = rotation_range

        self._rel_coord_anchor = pymunk.Vec2d(*position_anchor)
        self._rel_coord_part = pymunk.Vec2d(*position_part)

        self.set_relative_coordinates()
        self._attach_to_anchor()

    def _set_shape_collision(self):
        self.pm_visible_shape.collision_type = CollisionTypes.PART

    def _attach_to_anchor(self):
        self.joint = pymunk.PivotJoint(self.anchor.pm_body, self.pm_body,
                                       self._rel_coord_anchor,
                                       self._rel_coord_part)
        self.joint.collide_bodies = False
        self.limit = pymunk.RotaryLimitJoint(
            self.anchor.pm_body, self.pm_body,
            self.angle_offset - self.rotation_range / 2,
            self.angle_offset + self.rotation_range / 2)

        self.motor = pymunk.SimpleMotor(self.anchor.pm_body, self.pm_body, 0)

        self.pm_elements += [self.joint, self.motor, self.limit]

    def set_relative_coordinates(self):
        """
        Calculates the position of a Part relative to its Anchor.
        Sets the position of the Part.
        """

        self.pm_body.position = self.anchor.position + self._rel_coord_anchor.rotated(self.anchor.angle)\
                                - self._rel_coord_part.rotated(self.anchor.angle + self.angle_offset)
        self.pm_body.angle = self.anchor.pm_body.angle + self.angle_offset

    def reset(self):
        pass


class Head(AnchoredPart):
    """
    Circular Part, attached on its center.
    Not colliding with any Entity or Part.

    """
    def __init__(self,
                 anchor,
                 position_anchor=(0, 0),
                 angle_offset=0,
                 **kwargs):
        default_config = parse_configuration('agent_parts', PartTypes.HEAD)
        kwargs = {**default_config, **kwargs}

        super().__init__(anchor,
                         position_anchor=position_anchor,
                         angle_offset=angle_offset,
                         **kwargs)

        self.pm_visible_shape.sensor = True


class Eye(AnchoredPart):
    """
    Circular Part, attached on its center.
    Not colliding with any Entity or Part

    """
    def __init__(self,
                 anchor,
                 position_anchor=(0, 0),
                 angle_offset=0,
                 **kwargs):
        default_config = parse_configuration('agent_parts', PartTypes.EYE)
        kwargs = {**default_config, **kwargs}

        super().__init__(anchor,
                         position_anchor=position_anchor,
                         angle_offset=angle_offset,
                         **kwargs)

        self.pm_visible_shape.sensor = True


class Hand(AnchoredPart):
    """
    Circular Part, attached on its center.
    Is colliding with other Entity or Part, except from anchor and other Parts attached to it.

    """
    def __init__(self,
                 anchor,
                 position_anchor=(0, 0),
                 angle_offset=0,
                 **kwargs):
        default_config = parse_configuration('agent_parts', PartTypes.HAND)
        kwargs = {**default_config, **kwargs}

        super().__init__(anchor,
                         position_anchor=position_anchor,
                         angle_offset=angle_offset,
                         **kwargs)

        self.pm_visible_shape.sensor = True


class Arm(AnchoredPart):
    """
    Rectangular Part, attached on one extremity.
    Is colliding with other Entity or Part, except from anchor and other Parts attached to it.

    Attributes:
        extremity_anchor_point: coordinates of the free extremity, used to attach other Parts.

    """
    def __init__(self, anchor, position_anchor, angle_offset=0, **kwargs):
        default_config = parse_configuration('agent_parts', PartTypes.ARM)
        body_part_params = {**default_config, **kwargs}

        # arm attached at one extremity, and other anchor point defined at other extremity
        width, length = body_part_params['size']
        position_part = (-length / 2.0 + width / 2.0, 0)
        self.extremity_anchor_point = (+length / 2.0 - width / 2.0, 0)

        super().__init__(anchor=anchor,
                         position_anchor=position_anchor,
                         position_part=position_part,
                         angle_offset=angle_offset,
                         **body_part_params)

        self.motor.max_force = ARM_MAX_FORCE


class PartTypes(IntEnum):
    HEAD = auto()
    EYE = auto()
    ARM = auto()
    HAND = auto()
    PLATFORM = auto()
