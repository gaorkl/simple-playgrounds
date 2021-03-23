""" Module implementing Link.

A Link is a Part which can be attached to any other Part.
Links are controlled by angle.
Links do not collide with the Part (anchor) they are attached to.
"""

import math
from abc import ABC

import pymunk
from pymunk.vec2d import Vec2d

from simple_playgrounds.agents.parts.part import Part, Actuator
from simple_playgrounds.utils.definitions import ActionTypes, AgentPartTypes, ActionSpaces, ARM_MAX_FORCE, ANGULAR_VELOCITY
from simple_playgrounds.utils.parser import parse_configuration

# pylint: disable=line-too-long


class Link(Part, ABC):

    """
    Base class for Links.
    Contains methods to calculate coordinates of anchor points, create joints and motors between actuator and anchor.

    Attributes:
        anchor: Part on which the Actuator is attached

    """

    # pylint: disable=too-many-instance-attributes

    def __init__(self, anchor, position_anchor=(0, 0), position_part=(0, 0), angle_offset=0, **kwargs):

        """
        A Link is attached to an other Part (anchor).
        They are joined at a single point.
        A Link can never collide with its Anchor.
        A link has at least one actuator controlling its angular velocity.

        Args:
            anchor: Part on which the new Link will be attached
            position_anchor: relative position of the joint on the anchor. Default: (0,0)
            position_part: relative position of the joint on the part. Default: (0,0)
            angle_offset: angle offset of the link compared to the anchor (in rads). Default: 0
            **kwargs: additional Keyword Parameters

        """

        self.anchor = anchor

        default_config = parse_configuration('agent_parts', self.entity_type)
        body_part_params = {**default_config, **kwargs}

        super().__init__(**body_part_params)

        self._rotation_range = body_part_params['rotation_range']
        self._angle_offset = angle_offset

        self.rel_coord_anchor = Vec2d(*position_anchor)
        self.rel_coord_part = Vec2d(*position_part)

        self.set_relative_coordinates()

        self.joint = pymunk.PivotJoint(anchor.pm_body, self.pm_body, self.rel_coord_anchor, self.rel_coord_part)
        self.joint.collide_bodies = False
        self.limit = pymunk.RotaryLimitJoint(anchor.pm_body, self.pm_body,
                                               self._angle_offset - self._rotation_range / 2,
                                               self._angle_offset + self._rotation_range / 2)

        self.motor = pymunk.SimpleMotor(anchor.pm_body, self.pm_body, 0)

        self.pm_elements += [self.joint, self.motor, self.limit]

        self.angular_velocity_actuator = Actuator(self.name, ActionTypes.ANGULAR_VELOCITY,
                                                  ActionSpaces.CONTINUOUS_CENTERED)
        self.actuators.append(self.angular_velocity_actuator)

    def set_relative_coordinates(self):
        """
        Calculates the position of a Part relative to its Anchor.
        Sets the position of the Part.
        """

        self.pm_body.position = self.anchor.position + self.rel_coord_anchor.rotated(self.anchor.angle) \
                                 - self.rel_coord_part.rotated( self.anchor.angle + self._angle_offset)
        self.pm_body.angle = self.anchor.pm_body.angle + self._angle_offset

    def apply_action(self, actuator, value):

        super().apply_action(actuator, value)
        self._check_value_actuator(actuator, value)

        if actuator is self.angular_velocity_actuator:

            # Case when theta close to limit -> speed to zero
            theta_part = self.angle
            theta_anchor = self.anchor.angle

            angle_centered = (theta_part - (theta_anchor + self._angle_offset)) % (2 * math.pi)
            angle_centered = angle_centered - 2 * math.pi if angle_centered > math.pi else angle_centered

            # Do not set the motor if the limb is close to limit
            if angle_centered < - self._rotation_range/2 + math.pi/20 and value > 0:
                self.motor.rate = 0

            elif angle_centered > self._rotation_range/2 - math.pi/20 and value < 0:
                self.motor.rate = 0

            else:
                self.motor.rate = value * ANGULAR_VELOCITY

        return value


class Head(Link):
    """
    Circular Part, attached on its center.
    Not colliding with any Entity or Part.

    """
    entity_type = AgentPartTypes.HEAD

    def __init__(self, anchor, position_anchor=(0, 0), angle_offset=0, **kwargs):

        super().__init__(anchor, coord_anchor=position_anchor, angle_offset=angle_offset, **kwargs)

        self.pm_visible_shape.sensor = True


class Eye(Link):

    """
    Circular Part, attached on its center.
    Not colliding with any Entity or Part

    """
    entity_type = AgentPartTypes.EYE

    def __init__(self, anchor, position_anchor, angle_offset=0, **kwargs):

        super().__init__(anchor, position_anchor=position_anchor, angle_offset=angle_offset, **kwargs)

        self.pm_visible_shape.sensor = True


class Hand(Link):

    """
    Circular Part, attached on its center.
    Is colliding with other Entity or Part, except from anchor and other Parts attached to it.

    """
    entity_type = AgentPartTypes.HAND


class Arm(Link):
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
