from __future__ import annotations

import numpy as np
import pymunk
from gymnasium import spaces

from spg.core.definitions import ANGULAR_VELOCITY, LINEAR_FORCE

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
            filename=":spg:puzzle/elements/element_blue_square.png",
            sprite_front_is_up=True,
            shape_approximation="decomposition",
            **kwargs,
        )

        self.linear_ratio = LINEAR_FORCE * linear_ratio
        self.angular_ratio = ANGULAR_VELOCITY * angular_ratio

    def pre_step(self):
        super().pre_step()
        self._pm_body.apply_force_at_local_point((0, 0), (0, 0))
        self._pm_body.angular_velocity = 0

    def _apply_action(self, action):

        forward_force = action.get("forward_force", 0)
        angular_velocity = action.get("angular_velocity", 0)

        self._pm_body.apply_force_at_local_point(
            pymunk.Vec2d(forward_force, 0) * self.linear_ratio, (0, 0)
        )

        self._pm_body.angular_velocity = angular_velocity * self.angular_ratio

    @property
    def _action_space(self):

        return spaces.Dict(
            {"forward_force": spaces.Box(-1, 1), "angular_velocity": spaces.Box(-1, 1)}
        )


class Head(AnchoredPart):
    def __init__(self, **kwargs):
        super().__init__(
            mass=10,
            radius=10,
            filename=":spg:puzzle/elements/element_blue_polygon.png",
            sprite_front_is_up=True,
            **kwargs,
        )

    @property
    def _action_space(self):
        return spaces.Box(-1, 1)

    def pre_step(self):
        super().pre_step()
        self._motor.rate = 0

    def _apply_action(self, action):

        assert self._anchor
        assert self._motor
        angle_offset = self._anchor_coordinates[1]

        theta_part = self.angle
        theta_anchor = self._anchor.angle

        angle_centered = theta_part - (theta_anchor + angle_offset)
        angle_centered = angle_centered % (2 * np.pi)
        angle_centered = (
            angle_centered - 2 * np.pi if angle_centered > np.pi else angle_centered
        )

        # Do not set the motor if the limb is close to limit
        if (angle_centered < -self._rotation_range / 2 + np.pi / 20) and action < 0:
            self._motor.rate = 0

        elif (angle_centered > self._rotation_range / 2 - np.pi / 20) and action > 0:
            self._motor.rate = 0

        else:
            self._motor.rate = -action * ANGULAR_VELOCITY

    @property
    def _pivot_position(self):
        return (0, 0)


class Arm(AnchoredPart):
    def __init__(self, **kwargs):
        super().__init__(
            mass=10,
            filename=":resources:images/topdown_tanks/tankBlue_barrel3_outline.png",
            sprite_front_is_up=True,
            **kwargs,
        )

    @property
    def _action_space(self):
        return spaces.Box(-1, 1)

    def pre_step(self):
        super().pre_step()
        self._motor.rate = 0

    def _apply_action(self, action):

        assert self._anchor
        assert self._motor

        angle_offset = self._anchor_coordinates[1]

        theta_part = self.angle
        theta_anchor = self._anchor.angle

        angle_centered = theta_part - (theta_anchor + angle_offset)
        angle_centered = angle_centered % (2 * np.pi)
        angle_centered = (
            angle_centered - 2 * np.pi if angle_centered > np.pi else angle_centered
        )

        # Do not set the motor if the limb is close to limit
        if (angle_centered < -self._rotation_range / 2 + np.pi / 20) and action < 0:
            self._motor.rate = 0

        elif (angle_centered > self._rotation_range / 2 - np.pi / 20) and action > 0:
            self._motor.rate = 0

        else:
            self._motor.rate = -action * ANGULAR_VELOCITY

    @property
    def _pivot_position(self):
        return (-self.radius, 0)
