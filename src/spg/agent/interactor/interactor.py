from __future__ import annotations

from abc import abstractmethod
from typing import TYPE_CHECKING

from ..device import Device

if TYPE_CHECKING:
    from ...utils.position import Coordinate


INTERACTOR_RADIUS = 5


class Interactor(Device):
    def __init__(self, anchor, **kwargs):

        super().__init__(anchor=anchor, **kwargs)

        # Point on the anchor
        self._anchor_coordinates = ((0, 0), 0)

    @property
    def anchor_coordinates(self):
        return self._anchor_coordinates

    @anchor_coordinates.setter
    def anchor_coordinates(self, coord: Coordinate):
        self._anchor_coordinates = coord

    def relative_position(self):

        return (self.position - self._anchor.position).rotated(-self._anchor.angle)

    def relative_angle(self):
        return self.angle - self._anchor.angle


class ActiveInteractor(Interactor):
    @abstractmethod
    def apply_commands(self, **kwargs):
        ...
