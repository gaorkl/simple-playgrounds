"""
Module that defines Base Class SceneElement
"""
from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Optional

from ..entity import (
    Entity,
    Graspable,
    InteractiveAnchored,
    InteractiveZone,
    PhysicalEntity,
)
from ..utils.definitions import CollisionTypes


class SceneElement(ABC):
    pass


class PhysicalElement(PhysicalEntity, SceneElement):
    def __init__(self, **entity_params):
        super().__init__(**entity_params)

        self._interactives = []

        self._grasped_by = []
        self._graspable = False

        self._produced_by: Optional[Entity] = None

    @property
    def graspable(self):
        return bool(self._graspable)

    @graspable.setter
    def graspable(self, graspable: bool):
        if graspable and not self._graspable:
            self._graspable = Graspable(anchor=self)
            self.add(self._graspable)
        elif not graspable and self._graspable:
            assert self._playground
            self._playground.remove(self._graspable)
            self._graspable = False

    @property
    def grasped_by(self):
        return self._grasped_by

    @property
    def produced_by(self):
        return self._produced_by

    @property
    def interactives(self):
        return self._interactives

    def add(self, interactive: InteractiveAnchored):

        self._interactives.append(interactive)
        interactive.pm_body = self._pm_body
        interactive.teams = self._teams
        interactive.anchor = self

        if self._playground:
            self._playground.add(interactive)

    @property
    def _collision_type(self):
        return CollisionTypes.ELEMENT

    def update_team_filter(self):
        super().update_team_filter()

        for interactive in self._interactives:
            interactive.update_team_filter()

    # def update_sprite(self, view, sprite, force=False):
    #     super().update_sprite(view, sprite, force)

    # for interactive in self._interactives:
    #     interactive.update_sprite(view, sprite, force)

    # TODO: pre step, reset etc


class ZoneElement(InteractiveZone, SceneElement):
    pass


class RewardElement(ABC):
    @property
    @abstractmethod
    def _base_reward(self) -> float:
        ...

    @property
    def reward(self) -> float:
        return self._base_reward


class Teleporter(ZoneElement):
    pass
