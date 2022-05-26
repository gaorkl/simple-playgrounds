from __future__ import annotations
import math
from typing import Optional, TYPE_CHECKING

from simple_playgrounds.agent.controller import CenteredContinuousController
from tests.test_view.conftest import shape

if TYPE_CHECKING:
    from simple_playgrounds.agent.part.part import Part

import pymunk
import numpy as np

from simple_playgrounds.common.position_utils import Coordinate

from simple_playgrounds.common.definitions import ANGULAR_VELOCITY, CollisionTypes, LINEAR_FORCE
from simple_playgrounds.agent.agent import Agent
from simple_playgrounds.agent.part.part import AnchoredPart, InteractivePart, Platform

class MockBase(Platform):
  
    def __init__(self, agent: Agent, **kwargs):
        super().__init__(agent, mass=10,
                         filename=":resources:images/topdown_tanks/tankBody_blue_outline.png", sprite_front_is_up=True, shape_approximation = 'decomposition', **kwargs)

        self.forward_controller, self.angular_vel_controller = self._controllers

    def _set_controllers(self, **kwargs):

        control_forward = CenteredContinuousController(part=self)
        control_rotate = CenteredContinuousController(part=self)
        return control_forward, control_rotate

    def apply_commands(self, **kwargs):

        command_value = self.forward_controller.sample()

        self._pm_body.apply_force_at_local_point(
            pymunk.Vec2d(command_value, 0) * LINEAR_FORCE, (0, 0))

        command_value = self.angular_vel_controller.sample()
        self._pm_body.angular_velocity = command_value * ANGULAR_VELOCITY

    def post_step(self, **_):
        pass

class MockAnchoredPart(AnchoredPart):
    def __init__(self, anchor: Part, **kwargs):
        super().__init__(anchor, mass=10,
                         filename=":resources:images/topdown_tanks/tankBlue_barrel3_outline.png", **kwargs)
        self.joint_controller = self._controllers[0]

    def post_step(self, **_):
        return super().post_step(**_)

    def _set_controllers(self, **kwargs):
        return [CenteredContinuousController(part=self)]

    def apply_commands(self, **kwargs):

        value = self.joint_controller.sample()

        theta_part = self.angle
        theta_anchor = self._anchor.angle

        angle_centered = (theta_part - (theta_anchor + self._angle_offset))
        angle_centered = angle_centered % (2 * np.pi)
        angle_centered = (angle_centered - 2 * np.pi
                          if angle_centered > np.pi else angle_centered)

        # Do not set the motor if the limb is close to limit
        if (angle_centered < -self._rotation_range / 2 + np.pi / 20) and value < 0:
            self._motor.rate = 0

        elif (angle_centered > self._rotation_range / 2 - np.pi / 20) and value > 0:
            self._motor.rate = 0

        else:
            self._motor.rate = -value * ANGULAR_VELOCITY


class MockTriggerPart(InteractivePart):

    def __init__(self, anchor: Part, **kwargs):
        super().__init__(anchor, **kwargs)
        self._activated = False
    
    def pre_step(self):
        self._activated = False

    def _set_pm_collision_type(self):
        for pm_shape in self._pm_shapes:
            pm_shape.collision_type = CollisionTypes.TEST_TRIGGER
   
    def _set_controllers(self, **kwargs):
        return []

    def apply_commands(self, **kwargs):
        pass
    
    def post_step(self, **_):
        pass

    def trigger(self):
        self._activated = True



class MockAgent(Agent):

    def __init__(self, playground, initial_coordinates: Optional[Coordinate] = None, **kwargs):
        super().__init__(
            playground=playground,
            initial_coordinates=initial_coordinates,
            **kwargs)

        # MockTriggerPart(self._base, shape_approximation = 'decomposition')

    def _add_base(self, **kwargs) -> Part:
        base = MockBase(self, **kwargs)
        return base

    def post_step(self):
        pass

