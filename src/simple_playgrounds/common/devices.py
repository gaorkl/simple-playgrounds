from __future__ import annotations

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

    def pre_step(self):
        self._disabled = False

    def disable(self):
        self._disabled = True
        
    def add_to_playground(self, playground: Playground):
        if self._playground:
            raise ValueError('Entity {} already in a Playground'.format(self.name))

        self._playground = playground
        self._playground.space.add(*self.pm_elements)
