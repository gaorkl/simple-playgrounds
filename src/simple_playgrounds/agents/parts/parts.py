""" Module that defines the base class Part and Actuator.

Part inherits from Entity, and is used to create different body parts
of an agent. Parts are visible and movable by default.

Examples on how to add Parts to an agent can be found
in simple_playgrounds/agents/agents.py
"""
from __future__ import annotations
from typing import Tuple, List, TYPE_CHECKING, Optional

if TYPE_CHECKING:
    from simple_playgrounds.agents.parts.actuators import Actuator

import math
from abc import ABC
from enum import IntEnum, auto

import pymunk

from ...common.definitions import ARM_MAX_FORCE, CollisionTypes
from ...common.entity import Entity
from ...configs.parser import parse_configuration


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
        self.actuators: List[Actuator] = []

        self.agent = None

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
        can_absorb: bool = False,
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

        Part.__init__(self, can_absorb=can_absorb, movable=True, **kwargs)

        self._anchor: Optional[Part] = None
        self._angle_offset: Optional[float] = None
        self._rotation_range: Optional[float] = None
        self._position_on_anchor: Optional[pymunk.Vec2d] = None
        self._position_on_part: Optional[pymunk.Vec2d] = None

        self._attached = False

        self._motor = None

    def attach_to_anchor(self,
                         anchor: Part,
                         position_anchor: Tuple[float, float],
                         position_part: Tuple[float, float],
                         rotation_range: float,
                         angle_offset: float,
                         ):

        self._anchor = anchor
        self._angle_offset = angle_offset
        self._position_on_anchor = pymunk.Vec2d(*position_anchor)
        self._position_on_part = pymunk.Vec2d(*position_part)

        self._attached = True
        self.set_relative_coordinates()

        joint = pymunk.PivotJoint(self._anchor.pm_body, self.pm_body,
                                       self._position_on_anchor,
                                       self._position_on_part)
        joint.collide_bodies = False
        limit = pymunk.RotaryLimitJoint(
            self._anchor.pm_body, self.pm_body,
            self._angle_offset - rotation_range / 2,
            self._angle_offset + rotation_range / 2)

        self._motor = pymunk.SimpleMotor(self._anchor.pm_body, self.pm_body, 0)

        self.pm_elements += [joint, self._motor, limit]

    @property
    def motor(self):
        return self._motor

    def _set_shape_collision(self):
        self.pm_visible_shape.collision_type = CollisionTypes.PART

    def set_relative_coordinates(self):
        """
        Calculates the position of a Part relative to its Anchor.
        Sets the position of the Part.
        """

        self.pm_body.position = self._anchor.position + self._position_on_anchor.rotated(self._anchor.angle)\
                                - self._position_on_part.rotated(self._anchor.angle + self._angle_offset)
        self.pm_body.angle = self._anchor.pm_body.angle + self._angle_offset

    def reset(self):
        pass


class Head(AnchoredPart):
    """
    Circular Part, attached on its center.
    Not colliding with any Entity or Part.

    """
    def __init__(self,
                 **kwargs):
        default_config = parse_configuration('agent_parts', PartTypes.HEAD)
        kwargs = {**default_config, **kwargs}

        super().__init__(**kwargs)

        self.pm_visible_shape.sensor = True


class Eye(AnchoredPart):
    """
    Circular Part, attached on its center.
    Not colliding with any Entity or Part

    """
    def __init__(self,
                 **kwargs):
        default_config = parse_configuration('agent_parts', PartTypes.EYE)
        kwargs = {**default_config, **kwargs}

        super().__init__(**kwargs)

        self.pm_visible_shape.sensor = True


class Hand(AnchoredPart):
    """
    Circular Part, attached on its center.
    Is colliding with other Entity or Part, except from anchor and other Parts attached to it.

    """
    def __init__(self,
                 **kwargs):
        default_config = parse_configuration('agent_parts', PartTypes.HAND)
        kwargs = {**default_config, **kwargs}

        super().__init__(**kwargs)

        self.pm_visible_shape.sensor = True


class Arm(AnchoredPart):
    """
    Rectangular Part, attached on one extremity.
    Is colliding with other Entity or Part, except from anchor and other Parts attached to it.

    Attributes:
        extremity_anchor_point: coordinates of the free extremity, used to attach other Parts.

    """
    def __init__(self, **kwargs):
        default_config = parse_configuration('agent_parts', PartTypes.ARM)
        kwargs = {**default_config, **kwargs}

        # arm attached at one extremity, and other anchor point defined at other extremity
        width, length = kwargs['size']
        self.position_part = (-length / 2.0 + width / 2.0, 0)
        self.extremity_anchor_point = (+length / 2.0 - width / 2.0, 0)

        super().__init__(**kwargs)

        self.motor.max_force = ARM_MAX_FORCE

    def attach_to_anchor(self,
                         anchor: Part,
                         position_anchor: Tuple[float, float],
                         position_part: Tuple[float, float],
                         rotation_range: float,
                         angle_offset: float,
                         ):


class PartTypes(IntEnum):
    HEAD = auto()
    EYE = auto()
    ARM = auto()
    HAND = auto()
    PLATFORM = auto()
