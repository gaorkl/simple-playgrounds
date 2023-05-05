import math

import pymunk
from gym.vector.utils import spaces

from spg.entity import Agent, Entity
from spg.entity.mixin import BaseStaticMixin, AttachedDynamicMixin, ActionMixin, ActivableMixin, AttachedStaticMixin, \
    BaseDynamicMixin


class MockAgent(Agent, BaseDynamicMixin):

    def __init__(self, **kwargs):
        super().__init__(
        mass=30,
        filename=":spg:puzzle/element/element_blue_square.png",
        sprite_front_is_up=True,
        shape_approximation="decomposition",
        **kwargs,
    )

    def _apply_action(self, action):
        pass

    @property
    def action_space(self):
        return None

    @property
    def observation_space(self):
        return None





class MockAttachedPart(Entity, AttachedDynamicMixin, ActionMixin):

    def __init__(self, rotation_range, **kwargs):
        super().__init__(
            mass=1,
            filename=":resources:images/topdown_tanks/tankBlue_barrel3_outline.png",
            sprite_front_is_up=True,
            **kwargs,
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
        limit = pymunk.RotaryLimitJoint(
            self.anchor.pm_body,
            self.pm_body,
            relative_angle - self.rotation_range / 2,
            relative_angle + self.rotation_range / 2,
        )
        return limit

    def _get_motor(self):
        return pymunk.SimpleMotor(self.anchor.pm_body, self.pm_body, 0)

    @property
    def attachment_point(self):
        return -self.radius, 0

    @property
    def action_space(self):
        return spaces.Box(-1, 1, shape=(1,))

    def apply_action(self, action):
        self.motor.rate = action[0] * self.rotation_range


class Trigger(Entity, ActivableMixin, AttachedStaticMixin):

    def __init__(self, **kwargs):
        super().__init__(ghost=True, **kwargs)

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

class StaticAgent(Agent, BaseStaticMixin):
    pass


class StaticAgentWithArm(StaticAgent):
    def __init__(self, arm_position, arm_angle, **kwargs):

        super().__init__(**kwargs)

        self.arm = MockAttachedPart(rotation_range=math.pi/4)
        self.add(self.arm, arm_position, arm_angle)

class StaticAgentWithTrigger(StaticAgentWithArm):
    def __init__(self, arm_position, arm_angle, **kwargs):

        super().__init__(arm_position, arm_angle, **kwargs)

        self.trigger = Trigger()
        self.arm.add(self.trigger, (self.radius, 0))



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
