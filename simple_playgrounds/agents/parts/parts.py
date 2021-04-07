""" Module that defines the base class Part and Actuator.

Part inherits from Entity, and is used to create different body parts
of an agent. Parts are visible and movable by default.

Examples on how to add Parts to an agent can be found
in simple_playgrounds/agents/agents.py
"""

from abc import ABC
import math

import pymunk

from simple_playgrounds.entity import Entity
from simple_playgrounds.utils.definitions import AgentPartTypes, CollisionTypes, ARM_MAX_FORCE
from simple_playgrounds.utils.parser import parse_configuration

# pylint: disable=line-too-long


class Part(Entity, ABC):
    """
    Base class for Body Parts.
    Part inherits from Entity. It is a visible, movable Entity.

    An Anchored part is attached to an other Part (anchor).
    They are joined at a single point.
    A Part can never collide with its Anchor.
    """

    # pylint: disable=too-many-instance-attributes

    entity_type = AgentPartTypes.PART
    part_type = None
    movable = True
    background = False

    def __init__(self,
                 anchor,
                 position_anchor=(0, 0),
                 position_part=(0, 0),
                 rotation_range=math.pi/4,
                 angle_offset=0,
                 can_absorb=False,
                 **kwargs,
                 ):
        """

        Args:
            anchor (:obj:`Part`):
                Body Part on which the Part is attached
            position_anchor:
            position_part:
            rotation_range:
            angle_offset:
            can_absorb:
            **kwargs:
        """

        default_config = parse_configuration('agent_parts', self.entity_type)
        body_part_params = {**default_config, **kwargs}

        Entity.__init__(self, visible=True, movable=True, **body_part_params)
        self.pm_visible_shape.collision_type = CollisionTypes.AGENT

        self.can_absorb = can_absorb

        # Interactive parts
        self.is_eating = False
        self.is_activating = False

        self.can_grasp = False
        self.is_grasping = False
        self.is_holding = False
        self.grasped = []

        # For parts attached
        self.anchor = anchor
        self.angle_offset = angle_offset
        self.rotation_range = rotation_range
        self.motor = None

        # If part is attached to another part:
        if self.anchor:

            self._rel_coord_anchor = pymunk.Vec2d(*position_anchor)
            self._rel_coord_part = pymunk.Vec2d(*position_part)

            self.set_relative_coordinates()
            self._attach_to_anchor()

    def _attach_to_anchor(self):

        self.joint = pymunk.PivotJoint(self.anchor.pm_body, self.pm_body, self._rel_coord_anchor, self._rel_coord_part)
        self.joint.collide_bodies = False
        self.limit = pymunk.RotaryLimitJoint(self.anchor.pm_body, self.pm_body,
                                             self.angle_offset - self.rotation_range / 2,
                                             self.angle_offset + self.rotation_range / 2)

        self.motor = pymunk.SimpleMotor(self.anchor.pm_body, self.pm_body, 0)

        self.pm_elements += [self.joint, self.motor, self.limit]

    def set_relative_coordinates(self):
        """
        Calculates the position of a Part relative to its Anchor.
        Sets the position of the Part.
        """

        self.pm_body.position = self.anchor.position + self._rel_coord_anchor.rotated(self.anchor.angle) \
                                - self._rel_coord_part.rotated(self.anchor.angle + self.angle_offset)
        self.pm_body.angle = self.anchor.pm_body.angle + self.angle_offset

    def reset(self):

        super().reset()

        self.is_activating = False
        self.is_eating = False
        self.is_grasping = False
        self.grasped = []
        self.is_holding = False


# Platforms

class MobilePlatform(Part):
    """
        Platform that is moving.
        Can be used to build Arms with fixed base.
        Refer to the base class Platform.

    """
    entity_type = AgentPartTypes.PLATFORM

    def __init__(self, can_absorb, **kwargs):
        super().__init__(anchor=None, can_absorb=can_absorb, **kwargs)


class FixedPlatform(MobilePlatform):
    """
        Platform that is fixed.
        Can be used to build Arms with fixed base.
        Refer to the base class Platform.

    """
    movable = False


# Body parts


class Head(Part):
    """
    Circular Part, attached on its center.
    Not colliding with any Entity or Part.

    """
    entity_type = AgentPartTypes.HEAD

    def __init__(self, anchor, position_anchor=(0, 0), angle_offset=0, **kwargs):
        super().__init__(anchor, position_anchor=position_anchor, angle_offset=angle_offset, **kwargs)
        self.pm_visible_shape.sensor = True


class Eye(Head):

    """
    Circular Part, attached on its center.
    Not colliding with any Entity or Part

    """
    entity_type = AgentPartTypes.EYE


class Hand(Part):
    """
    Circular Part, attached on its center.
    Is colliding with other Entity or Part, except from anchor and other Parts attached to it.

    """
    entity_type = AgentPartTypes.HAND


class Arm(Part):
    """
    Rectangular Part, attached on one extremity.
    Is colliding with other Entity or Part, except from anchor and other Parts attached to it.

    Attributes:
        extremity_anchor_point: coordinates of the free extremity, used to attach other Parts.

    """
    entity_type = AgentPartTypes.ARM

    def __init__(self, anchor, position_anchor, angle_offset=0, **kwargs):

        default_config = parse_configuration('agent_parts', self.entity_type)
        body_part_params = {**default_config, **kwargs}

        # arm attached at one extremity, and other anchor point defined at other extremity
        width, length = body_part_params['width_length']
        position_part = [-length/2.0 + width/2.0, 0]
        self.extremity_anchor_point = [+length/2.0 - width/2.0, 0]

        super().__init__(anchor, position_anchor, position_part, angle_offset, **body_part_params)

        self.motor.max_force = ARM_MAX_FORCE


