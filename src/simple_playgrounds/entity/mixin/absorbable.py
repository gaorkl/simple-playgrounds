from abc import ABC, abstractmethod
from simple_playgrounds.entity.embodied import InteractionShape
from simple_playgrounds.common.definitions import CollisionTypes


class Absorber(InteractionShape, ABC):

    def absorb(self, absorbable):

        reward = absorbable.reward
        self._playground.remove(absorbable)

        self._assign_reward(reward)

    @abstractmethod
    def _assign_reward(self, reward):
        ...

    @staticmethod
    def _set_pm_collision_type(pm_shape):
        pm_shape.collision_type = CollisionTypes.ABSORBER


class Absorbable:

    def __init__(self,
                 reward: float
                 ):

        self._reward = reward

    @property
    def reward(self):
        return self._reward

    @staticmethod
    def _set_pm_collision_type(pm_shape):
        pm_shape.collision_type = CollisionTypes.ABSORBABLE

