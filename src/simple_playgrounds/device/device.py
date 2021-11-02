from __future__ import annotations
from typing import TYPE_CHECKING
from abc import ABC
import pymunk

if TYPE_CHECKING:
    from simple_playgrounds.common.definitions import RADIUS_DEVICE

from simple_playgrounds.common.definitions import CollisionTypes
from simple_playgrounds.common.entity import Entity


class Device(Entity, ABC):

    def __init__(self,
                 anchor: Entity,
                 **kwargs
                 ):

        Entity.__init__(**kwargs)

        self.pm_shape = pymunk.Circle(anchor.pm_body, RADIUS_DEVICE)
        self.pm_shape.sensor = True
        self.pm_shape.collision_type = CollisionTypes.DEVICE

        self._disabled: bool = False


        self._playground = anchor.playground

    def pre_step(self):
        self._disabled = False

    def disable(self):
        self._disabled = True

    def _add_to_playground(self):
        self._playground.space.add(self.pm_shape)

    def _remove_from_playground(self):
        self._playground.space.remove(self.pm_shape)
