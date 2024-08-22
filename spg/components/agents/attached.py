import math

import pymunk
from gymnasium import spaces

from spg.components.agents.constants import ANGULAR_VELOCITY, ARM_MASS, HEAD_MASS
from spg.core.entity import Entity
from spg.core.entity.body import AttachedDynamicMixin
from spg.core.entity.interaction.action import ActionMixin


class AttachedPart(Entity, AttachedDynamicMixin, ActionMixin):
    def __init__(self, rotation_range=math.pi / 3, **kwargs):
        self.rotation_range = rotation_range
        super().__init__(**kwargs)

    def _get_joint(self):
        joint = pymunk.PivotJoint(
            self.anchor.pm_body,
            self.pm_body,
            self.anchor.attachment_points[self][0],
            self.attachment_point,
        )
        joint.collide_bodies = False
        return joint

    def _get_limit(self):

        relative_angle = self.pm_body.angle - self.anchor.pm_body.angle

        limit = pymunk.RotaryLimitJoint(
            self.anchor.pm_body,
            self.pm_body,
            relative_angle - self.rotation_range / 2,
            relative_angle + self.rotation_range / 2,
        )
        limit.collide_bodies = False
        return limit

    def _get_motor(self):
        motor = pymunk.SimpleMotor(self.anchor.pm_body, self.pm_body, 0)
        motor.max_force = 5
        motor.collide_bodies = False
        return motor

    @property
    def _action_space(self):
        return spaces.Box(-1, 1, shape=(1,))

    def apply_action(self, action):
        self.motor.rate = action * ANGULAR_VELOCITY


class Arm(AttachedPart):
    def __init__(
        self,
        mass=ARM_MASS,
        rotation_range=math.pi / 4,
        filename=":spg:agent/arm.png",
        sprite_front_is_up=True,
        **kwargs
    ):

        super().__init__(
            mass=mass,
            rotation_range=rotation_range,
            sprite_front_is_up=sprite_front_is_up,
            filename=filename,
            **kwargs,
        )

    @property
    def attachment_point(self):
        return -self.radius, 0.0


class Head(AttachedPart):
    def __init__(
        self,
        mass=HEAD_MASS,
        filename=":spg:agent/head.png",
        sprite_front_is_up=True,
        rotation_range=math.pi / 2,
        **kwargs
    ):

        super().__init__(
            mass=mass,
            rotation_range=rotation_range,
            sprite_front_is_up=sprite_front_is_up,
            filename=filename,
            **kwargs,
        )

    @property
    def attachment_point(self):
        return 0, 0
