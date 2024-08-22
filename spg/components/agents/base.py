from abc import ABC

import pymunk
from gymnasium import spaces

from spg.core.entity import Agent
from spg.core.entity.body import BaseDynamicMixin, BaseStaticMixin

from .constants import ANGULAR_VELOCITY, BASE_MASS, LINEAR_FORCE


class DynamicAgent(Agent, BaseDynamicMixin, ABC):
    def __init__(self, **kwargs):
        super().__init__(
            sprite_front_is_up=True,
            filename=":spg:agent/base.png",
            shape_approximation="decomposition",
            mass=BASE_MASS,
            **kwargs,
        )


class HolonomicAgent(DynamicAgent, ABC):
    def _apply_action(self, action):

        forward_force, lateral_force, angular_velocity = action

        self.pm_body.apply_force_at_local_point(
            pymunk.Vec2d(forward_force, lateral_force) * LINEAR_FORCE, (0, 0)
        )

        self.pm_body.angular_velocity = angular_velocity * ANGULAR_VELOCITY


class HolonomicContinuousAgent(HolonomicAgent, ABC):
    @property
    def _action_space(self):
        return spaces.Box(low=-1, high=1, shape=(3,))


class HolonomicDiscreteAgent(HolonomicAgent, ABC):
    @property
    def _action_space(self):
        return spaces.MultiDiscrete([3, 3, 3], start=[-1, -1, -1])


class ForwardAgent(DynamicAgent, ABC):
    def _apply_action(self, action):

        forward_force, angular_velocity = action

        self.pm_body.apply_force_at_local_point(
            pymunk.Vec2d(forward_force, 0) * LINEAR_FORCE, (0, 0)
        )

        self.pm_body.angular_velocity = angular_velocity * ANGULAR_VELOCITY


class ForwardContinuousAgent(ForwardAgent, ABC):
    @property
    def _action_space(self):
        return spaces.Box(low=-1, high=1, shape=(2,))


class ForwardDiscreteAgent(ForwardAgent, ABC):
    @property
    def _action_space(self):
        return spaces.MultiDiscrete([3, 3], start=[-1, -1])


class StaticAgent(Agent, BaseStaticMixin, ABC):
    def __init__(self, **kwargs):
        super().__init__(
            sprite_front_is_up=True,
            filename=":spg:agent/base.png",
            shape_approximation="decomposition",
            **kwargs,
        )

    @property
    def _action_space(self):
        return None

    def _apply_action(self, action):
        pass
