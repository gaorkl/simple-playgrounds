import math

import pymunk
from gymnasium import spaces

from spg.agent.grasper import GraspableMixin, GrasperHold
from spg.definitions import ANGULAR_VELOCITY
from spg.entity import Agent, Entity
from spg.entity.mixin import (
    ActionMixin,
    ActivableMixin,
    AttachedDynamicMixin,
    AttachedStaticMixin,
    BaseDynamicMixin,
    BaseStaticMixin,
)
from spg.entity.mixin.sprite import get_texture_from_geometry
from tests.mock_entities import MockDynamicElement


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
        #
        # relative_angle = self.anchor.angle - self.angle
        #
        # angle_centered = relative_angle % (2 * math.pi)
        # angle_centered = (
        #     angle_centered - 2 * math.pi if angle_centered > math.pi else angle_centered
        # )
        #
        # # Do not set the motor if the limb is close to limit
        # if (angle_centered < -self.rotation_range / 2 + math.pi / 20) and action < 0:
        #     self.motor.rate = 0
        #
        # elif (angle_centered > self.rotation_range / 2 - math.pi / 20) and action > 0:
        #     self.motor.rate = 0

        pass


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

    def attachment_point(self):
        return 0, 0


class DynamicAgentWithGrasper(DynamicAgentWithArm):
    def __init__(self, arm_position, arm_angle, grasper_radius, **kwargs):

        super().__init__(arm_position, arm_angle, **kwargs)

        self.grasper = GrasperHand(grasper_radius=grasper_radius, traversable=True)
        self.arm.add(self.grasper, (self.arm.radius, 0))


class MockGraspable(MockDynamicElement, GraspableMixin):
    pass


#
# class Detector(Device):
#     def __init__(self, anchor, **kwargs):
#         super().__init__(anchor=anchor, **kwargs)
#         self._activated = False
#
#     @property
#     def _collision_type(self):
#         return CollisionTypes.PASSIVE_INTERACTOR
#
#     def pre_step(self):
#         self._activated = False
#
#     def activate(self):
#         self._activated = True
#
#     @property
#     def activated(self):
#         return self._activated
#
#     @property
#     def action_space(self):
#         return None
#
#     def apply_action(self):
#         pass
#
#
# class Trigger(Device):
#     def __init__(self, anchor, **kwargs):
#         super().__init__(anchor=anchor, **kwargs)
#
#         self._triggered = False
#
#     @property
#     def _collision_type(self):
#         return CollisionTypes.ACTIVE_INTERACTOR
#
#     def pre_step(self):
#         self._triggered = False
#
#     @property
#     def triggered(self):
#         return self._triggered
#
#     @property
#     def activated(self):
#         return self._triggered
#
#     @property
#     def action_space(self):
#         return spaces.Discrete(2)
#
#     def apply_action(self, action):
#
#         if action:
#             self._triggered = True
#
#
# class TriggerArm(Arm):
#     def __init__(self, **kwargs):
#
#         super().__init__(**kwargs)
#
#         self.trigger = Trigger(self, name="trigger")
#         self.add(self.trigger)
#
#
# class MockAgent(Agent):
#     def __init__(self, **kwargs):
#         super().__init__(**kwargs)
#
#     def _get_base(self):
#         return ForwardBase(name="base")
#
#     @property
#     def forward_action(self):
#
#         agent_forward_action = {self.name: {"base": {"motor": {"forward_force": 1}}}}
#         action = fill_action_space(self.playground, agent_forward_action)
#
#         return action
#
#
# class MockAgentWithArm(MockAgent):
#     def __init__(self, **kwargs):
#         super().__init__(**kwargs)
#
#         rel_left = ((15, 15), math.pi / 3)
#         self.left_arm = Arm(
#             name="left_arm",
#             rotation_range=math.pi / 4,
#         )
#         self.base.add(self.left_arm, rel_left)
#
#         rel_right = ((15, -15), -math.pi / 3)
#         self.right_arm = Arm(
#             name="right_arm",
#             rotation_range=math.pi / 4,
#         )
#         self.base.add(self.right_arm, rel_right)
#
#
# class MockAgentWithTriggerArm(MockAgent):
#     def __init__(self, **kwargs):
#         super().__init__(**kwargs)
#
#         rel_left = ((15, 15), math.pi / 3)
#         self.left_arm = TriggerArm(
#             name="left_arm",
#             rotation_range=math.pi / 4,
#         )
#         self.base.add(self.left_arm, rel_left)
#
#         rel_right = ((15, -15), -math.pi / 3)
#         self.right_arm = TriggerArm(
#             name="right_arm",
#             rotation_range=math.pi / 4,
#         )
#         self.base.add(self.right_arm, rel_right)
