from __future__ import annotations

import math

import numpy as np
import pymunk

from gymnasium import spaces

from spg.agent import Agent
from spg.agent.device import Device
from spg.agent.part import ForwardBase, Arm
from spg.utils.definitions import CollisionTypes


class Detector(Device):

    def __init__(self, anchor, **kwargs):
        super().__init__(anchor=anchor, **kwargs)
        self._activated = False

    @property
    def _collision_type(self):
        return CollisionTypes.PASSIVE_INTERACTOR

    def pre_step(self):
        self._activated = False

    def activate(self):
        self._activated = True

    @property
    def activated(self):
        return self._activated

    @property
    def action_space(self):
        return None

    def apply_action(self):
        pass


class Trigger(Device):
    def __init__(self, anchor, **kwargs):
        super().__init__(anchor=anchor, **kwargs)

        self._triggered = False

    @property
    def _collision_type(self):
        return CollisionTypes.ACTIVE_INTERACTOR

    def pre_step(self):
        self._triggered = False

    @property
    def triggered(self):
        return self._triggered

    @property
    def activated(self):
        return self._triggered

    @property
    def action_space(self):
        return spaces.Discrete(2)

    def apply_action(self, action):

        if action:
            self._triggered = True


class TriggerArm(Arm):

    def __init__(self, **kwargs):

        super().__init__(**kwargs)

        self.trigger = Trigger(self, name='trigger')
        self.add(self.trigger)


class MockAgent(Agent):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def _get_base(self):
        return ForwardBase(name="base")


class MockAgentWithArm(MockAgent):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        rel_left = ((15, 15), math.pi / 3)
        self.left_arm = Arm(
            name="left_arm",
            rotation_range=math.pi / 4,
        )
        self.base.add(self.left_arm, rel_left)

        rel_right = ((15, -15), -math.pi / 3)
        self.right_arm = Arm(
            name="right_arm",
            rotation_range=math.pi / 4,
        )
        self.base.add(self.right_arm, rel_right)


class MockAgentWithTriggerArm(MockAgent):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        rel_left = ((15, 15), math.pi / 3)
        self.left_arm = TriggerArm(
            name="left_arm",
            rotation_range=math.pi / 4,
        )
        self.base.add(self.left_arm, rel_left)

        rel_right = ((15, -15), -math.pi / 3)
        self.right_arm = TriggerArm(
            name="right_arm",
            rotation_range=math.pi / 4,
        )
        self.base.add(self.right_arm, rel_right)
