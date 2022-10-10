from __future__ import annotations

import math

import numpy as np
import pymunk

from spg.agent import Agent
from spg.agent.controller import BoolController, CenteredContinuousController
from spg.agent.interactor import Interactor
from spg.agent.part import AnchoredPart, PhysicalPart
from spg.utils.definitions import ANGULAR_VELOCITY, LINEAR_FORCE, CollisionTypes


class MockBase(PhysicalPart):
    def __init__(self, **kwargs):

        super().__init__(
            mass=10,
            filename=":resources:images/topdown_tanks/tankBody_blue_outline.png",
            sprite_front_is_up=True,
            shape_approximation="decomposition",
            **kwargs,
        )

        self.forward_controller = CenteredContinuousController("forward")
        self.add(self.forward_controller)

        self.angular_vel_controller = CenteredContinuousController("angular")
        self.add(self.angular_vel_controller)

    def _apply_commands(self, **kwargs):

        command_value = self.forward_controller.command_value

        self._pm_body.apply_force_at_local_point(
            pymunk.Vec2d(command_value, 0) * LINEAR_FORCE, (0, 0)
        )

        command_value = self.angular_vel_controller.command_value
        self._pm_body.angular_velocity = command_value * ANGULAR_VELOCITY


class MockAnchoredPart(AnchoredPart):
    def __init__(self, name_joint, **kwargs):
        super().__init__(
            mass=10,
            filename=":resources:images/topdown_tanks/tankBlue_barrel3_outline.png",
            sprite_front_is_up=True,
            **kwargs,
        )

        self.joint_controller = CenteredContinuousController(name_joint)
        self.add(self.joint_controller)

    def _apply_commands(self, **kwargs):

        assert self._anchor
        assert self._motor

        value = self.joint_controller.command_value
        angle_offset = self._anchor_coordinates[1]

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
        return (-self.radius, 0)


class MockHaloPart(Interactor):
    def __init__(self, anchor, **kwargs):
        super().__init__(anchor=anchor, **kwargs)
        self._activated = False

    @property
    def _collision_type(self):
        return CollisionTypes.PASSIVE_INTERACTOR

    def _apply_commands(self, **_):
        pass

    def pre_step(self):
        self._activated = False

    def activate(self):
        self._activated = True

    @property
    def activated(self):
        return self._activated


class MockInteractor(Interactor):
    def __init__(self, anchor, **kwargs):
        super().__init__(anchor=anchor, **kwargs)

        self._activated = False

    @property
    def _collision_type(self):
        return CollisionTypes.ACTIVE_INTERACTOR

    def pre_step(self):
        self._activated = False

    def activate(self):
        self._activated = True

    @property
    def activated(self):
        return self._activated


class MockTriggerPart(MockAnchoredPart):
    def __init__(self, name_joint, rotation_range: float, **kwargs):

        super().__init__(name_joint=name_joint, rotation_range=rotation_range, **kwargs)

        self.interactor = MockInteractor(self)
        self.add(self.interactor)

        self.trigger = BoolController(name_joint + "_trigger")
        self.add(self.trigger)

    def _apply_commands(self, **_):

        if self.trigger.command_value:
            self.interactor.activate()


class MockAgent(Agent):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        base = MockBase()
        self.add(base)


class MockAgentWithArm(MockAgent):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        rel_left = ((15, 15), math.pi / 3)
        self.left_arm = MockAnchoredPart(
            "left_joint",
            rotation_range=math.pi / 4,
        )
        self.base.add(self.left_arm, rel_left)

        rel_right = ((15, -15), -math.pi / 3)
        self.right_arm = MockAnchoredPart(
            "right_joint",
            rotation_range=math.pi / 4,
        )
        self.base.add(self.right_arm, rel_right)


class MockAgentWithTriggerArm(MockAgent):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        rel_left = ((15, 15), math.pi / 3)
        self.left_arm = MockTriggerPart(
            "left_joint",
            rotation_range=math.pi / 4,
        )
        self.base.add(self.left_arm, rel_left)

        rel_right = ((15, -15), -math.pi / 3)
        self.right_arm = MockTriggerPart(
            "right_joint",
            rotation_range=math.pi / 4,
        )
        self.base.add(self.right_arm, rel_right)
