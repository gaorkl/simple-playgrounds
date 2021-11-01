from abc import ABC, abstractmethod
from typing import Optional, Any

from simple_playgrounds.entity.embodied import InteractionShape
from simple_playgrounds.common.definitions import CollisionTypes


class Activator(InteractionShape):

    @staticmethod
    def _set_pm_collision_type(pm_shape):
        pm_shape.collision_type = CollisionTypes.ACTIVATOR


class Activable(InteractionShape):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._activated_by: Optional[Any] = None

    def pre_step(self):
        self._activated_by = None

    def activate(self, activator):
        self._activate(activator)
        self._activated_by = activator

    @abstractmethod
    def _activate(self, activator):
        ...

    @property
    def activated_by(self):
        return self._activated_by

    @property
    def activated(self):
        return bool(self._activated_by)

    @staticmethod
    def _set_pm_collision_type(pm_shape):
        pm_shape.collision_type = CollisionTypes.ACTIVABLE

    def reset(self):
        self.pre_step()
