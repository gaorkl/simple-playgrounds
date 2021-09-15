from abc import ABC, abstractmethod

import pymunk

from simple_playgrounds.common.entity import Entity
from simple_playgrounds.common.definitions import CollisionTypes

_RADIUS_DEVICE = 5


class Device:

    def __init__(self,
                 anchor: Entity,
                 ):

        self._anchor = anchor
        self.pm_shape = pymunk.Circle(anchor.pm_body, _RADIUS_DEVICE)

        self._disabled: bool = False

    def _set_shape_collision(self):
        self.pm_shape.collision_type = CollisionTypes.DEVICE

    def pre_step(self):
        self._disabled = False

    def disable(self):
        self._disabled = True

