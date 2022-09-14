from __future__ import annotations

import numpy as np
import pymunk

from ...utils.definitions import ANGULAR_VELOCITY, LINEAR_FORCE
from ..controller import CenteredContinuousController
from .part import AnchoredPart, PhysicalPart


class ForwardBase(PhysicalPart):
    def __init__(
        self,
        linear_ratio: float = 1,
        angular_ratio: float = 1,
        **kwargs,
    ):

        super().__init__(
            mass=30,
            filename=":spg:puzzle/element/element_blue_square.png",
            sprite_front_is_up=True,
            shape_approximation="decomposition",
            **kwargs,
        )

        self.forward_controller = CenteredContinuousController()
        self.add(self.forward_controller)

        self.angular_vel_controller = CenteredContinuousController()
        self.add(self.angular_vel_controller)

        self.linear_ratio = LINEAR_FORCE * linear_ratio
        self.angular_ratio = ANGULAR_VELOCITY * angular_ratio

    def _apply_commands(self, **kwargs):

        command_value = self.forward_controller.command_value

        self._pm_body.apply_force_at_local_point(
            pymunk.Vec2d(command_value, 0) * self.linear_ratio, (0, 0)
        )

        command_value = self.angular_vel_controller.command_value
        self._pm_body.angular_velocity = command_value * self.angular_ratio


class Head(AnchoredPart):
    def __init__(self, **kwargs):
        super().__init__(
            mass=10,
            radius=10,
            filename=":spg:puzzle/element/element_blue_polygon.png",
            sprite_front_is_up=True,
            **kwargs,
        )
        self.joint_controller = CenteredContinuousController()
        self.add(self.joint_controller)

    def _apply_commands(self, **kwargs):

        assert self._anchor
        assert self._motor
        angle_offset = self._anchor_coordinates[1]

        value = self.joint_controller.command_value

        theta_part = self.angle
        theta_anchor = self._anchor.angle

        angle_centered = theta_part - (theta_anchor + angle_offset)
        angle_centered = angle_centered % (2 * np.pi)
        angle_centered = (
            angle_centered - 2 * np.pi if angle_centered > np.pi else angle_centered
        )

        # Do not set the motor if the limb is close to limit
        if (angle_centered < -self._rotation_range / 2 + np.pi / 20) and value < 0:
            self._motor.rate = 0

        elif (angle_centered > self._rotation_range / 2 - np.pi / 20) and value > 0:
            self._motor.rate = 0

        else:
            self._motor.rate = -value * ANGULAR_VELOCITY

    @property
    def _pivot_position(self):
        return (0, 0)
