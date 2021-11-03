from __future__ import annotations
from typing import TYPE_CHECKING, Optional
if TYPE_CHECKING:
    from simple_playgrounds.playground.playground import Playground

from abc import ABC

import pymunk

from simple_playgrounds.common.entity import Entity
from simple_playgrounds.common.definitions import CollisionTypes

_RADIUS_DEVICE = 5


class Device(ABC):

    def __init__(self,
                 anchor: Entity,
                 ):

        self._anchor = anchor
        self.pm_shape = pymunk.Circle(anchor.pm_body, _RADIUS_DEVICE)
        self.pm_shape.sensor = True

        self._disabled: bool = False

        self.pm_shape.collision_type = CollisionTypes.DEVICE

        self._playground: Optional[Playground] = None

        # if anchor already in playground
        if anchor.playground:
            self._playground = anchor.playground

    @property
    def playground(self):
        return self._playground

    @playground.setter
    def playground(self, pg):
        self._playground = pg

    @property
    def in_playground(self):
        return bool(self._playground)

    def pre_step(self):
        self._disabled = False

    def disable(self):
        self._disabled = True
