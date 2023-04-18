from __future__ import annotations

from typing import Optional, Tuple
from abc import abstractmethod, ABC
from pymunk import Circle
from gymnasium import spaces

from spg.utils.sprite import get_texture_from_shape

from ...entity import InteractiveAnchored
from ...utils.definitions import CollisionTypes

DEVICE_RADIUS = 5


class Device(InteractiveAnchored, ABC):
    def __init__(
        self,
        name,
        **kwargs,
    ):
        super().__init__(
            name = name, **kwargs,
        )
        self._disabled = False

    @property
    def teams(self):
        return self._teams

    @teams.setter
    def teams(self, teams):
        self._teams = teams

    @property
    def _collision_type(self):
        return CollisionTypes.DEVICE

    def pre_step(self):
        self._disabled = False

    def disable(self):
        self._disabled = True

    @property
    def agent(self):
        assert self._anchor
        return self._anchor.agent

    @property
    @abstractmethod
    def action_space(self) -> spaces.Space:
        ...

    @abstractmethod
    def apply_action(self, action):
        ...


class PocketDevice(Device):
    def __init__(
        self,
        color: Optional[Tuple[int, int, int]] = None,
        radius: float = DEVICE_RADIUS,
        **kwargs,
    ):

        pm_shape = Circle(None, DEVICE_RADIUS)
        texture = get_texture_from_shape(
            pm_shape, color, f"Device_{DEVICE_RADIUS}_{color}"
        )
        shape_approximation = "circle"
        radius = DEVICE_RADIUS

        super().__init__(
            texture=texture,
            shape_approximation=shape_approximation,
            radius=radius,
            **kwargs,
        )
