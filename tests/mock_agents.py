from __future__ import annotations
from typing import Optional, TYPE_CHECKING

from simple_playgrounds.agent.controller import CenteredContinuousController

if TYPE_CHECKING:
    from simple_playgrounds.agent.part.part import Part

import pymunk
from simple_playgrounds.common.position_utils import Coordinate

from simple_playgrounds.entity.embodied.interactive import StandAloneInteractive, AnchoredInteractive
from simple_playgrounds.common.definitions import ANGULAR_VELOCITY, CollisionTypes, LINEAR_FORCE, PymunkCollisionCategories
from simple_playgrounds.playground.collision_handlers import get_colliding_entities
from simple_playgrounds.entity.embodied.appearance.texture import ColorTexture
from simple_playgrounds.agent.agent import Agent
from simple_playgrounds.agent.part.part import CommandDict, Platform

class MockBase(Platform):
  
    def __init__(self, agent: Agent, **kwargs):
        super().__init__(agent, **kwargs)

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


class MockAgent(Agent):

    def __init__(self, playground, coordinates: Optional[Coordinate] = None, **kwargs):
        super().__init__(
            playground=playground,
            initial_coordinates=coordinates,
            appearance=ColorTexture(color=(121, 10, 220)), 
            shape='circle',
            radius=4,
            movable=True,
            mass=10,
            **kwargs)

    def _add_base(self, **kwargs) -> Part:
        base = MockBase(self, **kwargs)
        return base

    def post_step(self):
        pass

