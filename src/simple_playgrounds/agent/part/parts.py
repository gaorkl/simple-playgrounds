from __future__ import annotations

from simple_playgrounds.agent.part.controller import (
    CenteredContinuousController,
)

import pymunk
import numpy as np


from simple_playgrounds.common.definitions import (
    ANGULAR_VELOCITY,
    LINEAR_FORCE,
)
from simple_playgrounds.agent.agent import Agent
from simple_playgrounds.agent.part.part import (
    AnchoredPart,
    PhysicalPart,
    Platform,
)


class ForwardBase(Platform):
    def __init__(
        self,
        agent: Agent,
        linear_ratio: float = 1,
        angular_ratio: float = 1,
        **kwargs,
    ):

        super().__init__(
            agent,
            mass=30,
            filename=":spg:puzzle/element/element_blue_square.png",
            sprite_front_is_up=True,
            shape_approximation="decomposition",
            **kwargs,
        )

        self.forward_controller, self.angular_vel_controller = self._controllers
        self.linear_ratio = LINEAR_FORCE * linear_ratio
        self.angular_ratio = ANGULAR_VELOCITY * angular_ratio

    def _set_controllers(self, **kwargs):

        control_forward = CenteredContinuousController(part=self)
        control_rotate = CenteredContinuousController(part=self)
        return control_forward, control_rotate

    def apply_commands(self, **kwargs):

        command_value = self.forward_controller.command_value

        self._pm_body.apply_force_at_local_point(
            pymunk.Vec2d(command_value, 0) * self.linear_ratio, (0, 0)
        )

        command_value = self.angular_vel_controller.command_value
        self._pm_body.angular_velocity = command_value * self.angular_ratio


class Head(AnchoredPart):
    def __init__(self, anchor: PhysicalPart, **kwargs):
        super().__init__(
            anchor,
            mass=10,
            radius=10,
            filename=":spg:puzzle/element/element_blue_polygon.png",
            sprite_front_is_up=True,
            relative_angle=0,
            **kwargs,
        )
        self.joint_controller = self._controllers[0]

    def _set_controllers(self, **kwargs):
        return [CenteredContinuousController(part=self)]

    def apply_commands(self, **kwargs):

        value = self.joint_controller.command_value

        theta_part = self.angle
        theta_anchor = self._anchor.angle

        angle_centered = theta_part - (theta_anchor + self._angle_offset)
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
    def default_position_on_part(self):
        return (0, 0)
