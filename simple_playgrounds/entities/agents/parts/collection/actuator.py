"""
Body Parts of an Agent.
"""

import math
from abc import ABC

import pymunk
import pygame

from simple_playgrounds.entities.agents.parts.part import Part
from simple_playgrounds.utils import ActionTypes, Action

# pylint: disable=line-too-long


class Actuator(Part, ABC):

    """
    Base class for Actuators.
    Contains methods to calculate coordinates of anchor points, create joints and motors between actuator and anchor.

    Attributes:
        anchor: Entity on which the Actuator is attached

    """

    #pylint: disable=too-many-instance-attributes

    def __init__(self, anchor, coord_anchor=(0, 0), coord_part=(0, 0), angle_offset=0, **kwargs):

        """
        An Actuator is attached to an other Part (anchor).
        They are joined at a single point.
        An Actuator can never collide with its Anchor.

        Args:
            anchor: Part on which the new Actuator will be attached
            coord_anchor: coordinates of the joint on the anchor. Default: (0,0)
            coord_part: coordinates of the joint on the actuator. Default: (0,0)
            angle_offset: angle offset of the actuator compared to the anchor (in rads). Default: 0
            **kwargs: additional Keyword Parameters

        Keyword Args:
            max_angular_velocity: relative angular velocity of the actuator (rads per timestep)
            rotation_range: limits the relative angle between actuator and anchor, centered on angle_offset (degrees)
        """

        self.anchor = anchor

        super().__init__(**kwargs)

        self.max_angular_velocity = kwargs['max_angular_velocity']
        self.rotation_range = kwargs['rotation_range']

        self.angle_offset = angle_offset

        self.relative_position_of_anchor_on_anchor = coord_anchor
        self.relative_position_of_anchor_on_part = coord_part

        self.set_relative_position()

        x_0, y_0 = self.relative_position_of_anchor_on_anchor
        x_1, y_1 = self.relative_position_of_anchor_on_part

        self.joint = pymunk.PivotJoint(anchor.pm_body, self.pm_body, (y_0, -x_0), (y_1, -x_1))
        self.joint.collide_bodies = False
        self.limit = pymunk.RotaryLimitJoint(anchor.pm_body, self.pm_body,
                                             self.angle_offset - self.rotation_range/2,
                                             self.angle_offset + self.rotation_range/2)

        self.motor = pymunk.SimpleMotor(anchor.pm_body, self.pm_body, 0)

        self.pm_elements += [self.joint, self.motor, self.limit]

    def set_relative_position(self):
        """
        Calculates the position of a Part relative to its Anchor.
        Sets the position of the Part.
        """
        # Get position of the anchor point on anchor
        x_anchor_center, y_anchor_center = self.anchor.pm_body.position
        x_anchor_center, y_anchor_center = -y_anchor_center, x_anchor_center
        theta_anchor = (self.anchor.pm_body.angle + math.pi / 2) % (2 * math.pi)

        x_anchor_relative_of_anchor, y_anchor_relative_of_anchor = self.relative_position_of_anchor_on_anchor

        x_anchor_coordinates_anchor = (x_anchor_center + x_anchor_relative_of_anchor*math.cos(theta_anchor - math.pi/2)
                                       - y_anchor_relative_of_anchor*math.sin(theta_anchor - math.pi/2))
        y_anchor_coordinates_anchor = (y_anchor_center + x_anchor_relative_of_anchor*math.sin(theta_anchor - math.pi/2)
                                       + y_anchor_relative_of_anchor*math.cos(theta_anchor - math.pi/2))

        # Get position of the anchor point on part
        theta_part = (self.anchor.pm_body.angle + self.angle_offset + math.pi / 2) % (2 * math.pi)

        x_anchor_relative_of_part, y_anchor_relative_of_part = self.relative_position_of_anchor_on_part

        x_anchor_coordinates_part = (x_anchor_relative_of_part * math.cos(theta_part - math.pi / 2)
                                     - y_anchor_relative_of_part * math.sin(theta_part - math.pi / 2))
        y_anchor_coordinates_part = (x_anchor_relative_of_part * math.sin(theta_part - math.pi / 2)
                                     + y_anchor_relative_of_part * math.cos(theta_part - math.pi / 2))

        # Move part to align on anchor
        pos_y = -(x_anchor_coordinates_anchor - x_anchor_coordinates_part)
        pos_x = y_anchor_coordinates_anchor - y_anchor_coordinates_part
        self.pm_body.position = (pos_x, pos_y)

        self.pm_body.angle = self.anchor.pm_body.angle + self.angle_offset

    def get_available_actions(self):

        actions = super().get_available_actions()

        actions.append(Action(self.name, ActionTypes.ANGULAR_VELOCITY, ActionTypes.CONTINUOUS_CENTERED, -1, 1))

        return actions

    def apply_actions(self, actions):

        super().apply_actions(actions)

        angular_velocity = actions.get(ActionTypes.ANGULAR_VELOCITY, 0)

        self.motor.rate = angular_velocity * self.max_angular_velocity

        # Case when theta close to limit -> speed to zero
        theta_part = self.position[2]
        theta_anchor = self.anchor.position[2]

        angle_centered = (theta_part - (theta_anchor+self.angle_offset)) % (2*math.pi)
        angle_centered = angle_centered - 2 * math.pi if angle_centered > math.pi else angle_centered

        # Do not set the motor if the limb is close to limit
        if angle_centered < - self.rotation_range/2 + math.pi/20 and angular_velocity > 0:
            self.motor.rate = 0

        elif angle_centered > self.rotation_range/2 - math.pi/20 and angular_velocity < 0:
            self.motor.rate = 0


class Head(Actuator):
    """
    Circular Part, attached on its center.
    Not colliding with any Entity or Part.

    """

    def __init__(self, anchor, position_anchor=(0, 0), angle_offset=0, **kwargs):

        default_config = self._parse_configuration('head')
        body_part_params = {**default_config, **kwargs}

        super(Head, self).__init__(anchor, coord_anchor=position_anchor, angle_offset=angle_offset, **body_part_params)

        self.pm_visible_shape.sensor = True

    # def _create_mask(self, is_interactive=False):
    #
    #     mask = super()._create_mask()
    #
    #     pos_y = self.radius + (self.radius - 2) * (math.cos(self.pm_body.angle))
    #     pos_x = self.radius + (self.radius - 2) * (math.sin(self.pm_body.angle))
    #     pygame.draw.line(mask, pygame.color.THECOLORS["green"], (self.radius, self.radius), (pos_x, pos_y), 2)
    #
    #     return mask


class Eye(Actuator):

    """
    Circular Part, attached on its center.
    Not colliding with any Entity or Part

    """

    def __init__(self, anchor, position_anchor, angle_offset=0, **kwargs):

        default_config = self._parse_configuration('eye')
        body_part_params = {**default_config, **kwargs}

        super(Eye, self).__init__(anchor, coord_anchor=position_anchor, angle_offset=angle_offset, **body_part_params)

        self.pm_visible_shape.sensor = True

    # def _create_mask(self, is_interactive=False):
    #
    #     mask = super()._create_mask()
    #
    #     pos_y = self.radius + (self.radius - 2) * (math.cos(self.pm_body.angle))
    #     pos_x = self.radius + (self.radius - 2) * (math.sin(self.pm_body.angle))
    #     pygame.draw.line(mask, pygame.color.THECOLORS["brown"], (self.radius, self.radius), (pos_x, pos_y), 2)
    #
    #     return mask


class Hand(Actuator):

    """
    Circular Part, attached on its center.
    Is colliding with other Entity or Part, except from anchor and other Parts attached to it.

    """

    def __init__(self, anchor, position_anchor, angle_offset=0, **kwargs):

        default_config = self._parse_configuration('hand')
        body_part_params = {**default_config, **kwargs}

        super(Hand, self).__init__(anchor, coord_anchor=position_anchor, angle_offset=angle_offset, **body_part_params)


class Arm(Actuator):
    """
    Rectangular Part, attached on one extremity.
    Is colliding with other Entity or Part, except from anchor and other Parts attached to it.

    Attributes:
        extremity_anchor_point: coordinates of the free extremity, used to attach other Parts.

    """

    def __init__(self, anchor, position_anchor, angle_offset=0, **kwargs):

        default_config = self._parse_configuration('arm')
        body_part_params = {**default_config, **kwargs}

        # arm attached at one extremity, and other anchr point defined at other extremity
        width, length = body_part_params['width_length']
        position_part = [0, -length/2.0 + width/2.0]

        self.extremity_anchor_point = [0, length/2.0 - width/2.0]

        super(Arm, self).__init__(anchor, position_anchor, position_part, angle_offset, **body_part_params)

        self.motor.max_force = 500
