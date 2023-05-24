from __future__ import annotations

from abc import abstractmethod
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    pass

from spg.core.collision import CollisionTypes


class ActivableMixin:

    activated = False
    collision_type = CollisionTypes.ACTIVABLE

    @abstractmethod
    def activate(self, entity, **kwargs):
        ...


