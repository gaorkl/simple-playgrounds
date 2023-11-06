import math

import pymunk
from gymnasium import spaces

from spg.components.grasper import GraspableMixin, GrasperHold
from spg.core.entity import Agent, Entity
from spg.core.entity.action import ActionMixin
from spg.core.entity.mixin import (
    ActivableMixin,
    AttachedDynamicMixin,
    AttachedStaticMixin,
    BaseDynamicMixin,
    BaseStaticMixin,
)
from spg.core.entity.mixin.sprite import get_texture_from_geometry
from spg.core.sensor.ray.ray import RaySensor
from tests.mock_entities import MockDynamicElement

ANGULAR_VELOCITY = 0.3


class MockAgent(Agent):
    def __init__(self, **kwargs):
        super().__init__(
            filename=":spg:puzzle/element/element_blue_square.png",
            sprite_front_is_up=True,
            shape_approximation="decomposition",
            **kwargs,
        )

    def apply_action(self, action):

        forward_force, lateral_force, angular_velocity = action

        self.pm_body.apply_force_at_local_point(
            pymunk.Vec2d(forward_force, lateral_force) * 100, (0, 0)
        )

        self.pm_body.angular_velocity = angular_velocity * 0.3

    @property
    def action_space(self):
        return spaces.Box(low=-1, high=1, shape=(3,))

    @property
    def observation_space(self):
        return None


class MockAttachedPart(Entity, AttachedDynamicMixin, ActionMixin):
    def __init__(self, rotation_range, **kwargs):
        super().__init__(
            mass=1,
            filename=":resources:images/topdown_tanks/tankBlue_barrel3_outline.png",
            sprite_front_is_up=True,
        )

        self.rotation_range = rotation_range

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

        relative_angle = self.anchor.attachment_points[self][1]
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
        motor.max_force = 10
        motor.collide_bodies = False
        return motor

    @property
    def attachment_point(self):
        return -self.radius, 0.0

    @property
    def action_space(self):
        return spaces.Box(-1, 1, shape=(1,))

    def apply_action(self, action):
        self.motor.rate = action * ANGULAR_VELOCITY


class Trigger(Entity, ActivableMixin, AttachedStaticMixin):
    def __init__(self, **kwargs):

        texture, _ = get_texture_from_geometry(
            geometry="circle", radius=20, color=(255, 0, 0)
        )

        super().__init__(ghost=True, texture=texture, **kwargs)

        self.triggered = False

    def activate(self, entity, **kwargs):
        self.activated = True

    def pre_step(self):
        self.triggered = False
        super().pre_step()

    @property
    def attachment_point(self):
        return 0, 0

    @property
    def action_space(self):
        return spaces.Discrete(2)

    def apply_action(self, action):
        if action == 1:
            self.triggered = True


class StaticAgent(MockAgent, BaseStaticMixin):
    pass


class StaticAgentWithArm(StaticAgent):
    def __init__(self, arm_position, arm_angle, **kwargs):

        super().__init__(**kwargs)

        self.arm = MockAttachedPart(rotation_range=math.pi / 4)
        self.add(self.arm, arm_position, arm_angle)


class StaticAgentWithTrigger(StaticAgentWithArm):
    def __init__(self, arm_position, arm_angle, **kwargs):

        super().__init__(arm_position, arm_angle, **kwargs)

        self.trigger = Trigger()
        self.arm.add(self.trigger, (self.radius, 0))


class DynamicAgent(MockAgent, BaseDynamicMixin):
    def __init__(self, **kwargs):
        super().__init__(mass=10, **kwargs)


class DynamicAgentWithArm(DynamicAgent):
    def __init__(self, arm_position, arm_angle, rotation_range, **kwargs):

        super().__init__(**kwargs)

        self.arm = MockAttachedPart(rotation_range=rotation_range)
        self.add(self.arm, arm_position, arm_angle)


class DynamicAgentWithTrigger(DynamicAgentWithArm):
    def __init__(self, arm_position, arm_angle, **kwargs):

        super().__init__(arm_position, arm_angle, **kwargs)

        self.trigger = Trigger()
        self.arm.add(self.trigger, (self.radius, 0))


class GrasperHand(Entity, AttachedStaticMixin, GrasperHold):
    def __init__(self, grasper_radius, **kwargs):

        texture, _ = get_texture_from_geometry(
            geometry="circle", radius=grasper_radius, color=(255, 0, 0)
        )

        super().__init__(
            texture=texture,
            ghost=True,
            **kwargs,
        )

    @property
    def attachment_point(self):
        return 0, 0


class DynamicAgentWithGrasper(DynamicAgentWithArm):
    @property
    def observation(self):
        pass

    def __init__(self, arm_position, arm_angle, grasper_radius, **kwargs):

        super().__init__(arm_position, arm_angle, **kwargs)

        self.grasper = GrasperHand(grasper_radius=grasper_radius, traversable=True)
        self.arm.add(self.grasper, (self.arm.radius, 0))


class MockGraspable(MockDynamicElement, GraspableMixin):
    pass


class MockRaySensor(Entity, AttachedStaticMixin, RaySensor):
    def _convert_hitpoints_to_observation(self):
        return self._hitpoints

    def _get_ray_colors(self):
        pass

    def __init__(self, **kwargs):

        texture, _ = get_texture_from_geometry(
            geometry="circle", radius=10, color=(255, 0, 0)
        )

        super().__init__(
            texture=texture,
            transparent=True,
            **kwargs,
        )

        RaySensor.__init__(self, **kwargs)

    @property
    def observation_space(self):
        return spaces.Box(low=0, high=255 + 255**2 + 255**3, shape=(13,))

    @property
    def attachment_point(self):
        return 0, 0
