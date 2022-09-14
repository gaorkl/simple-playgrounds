""" Contains the base class for entities.

Entity classes should be used to create body parts of
an agent, scene entities, spawners, timers, etc.

Entity is the generic building block of physical and interactive
objects in simple-playgrounds.

"""
from __future__ import annotations

from abc import ABC
from typing import TYPE_CHECKING, List, Optional, Union

if TYPE_CHECKING:
    from ..playground import Playground

Teams = Union[str, List[str]]


class Entity(ABC):
    """
    Base class that defines the entities that composing a Playground.
    Entities can be: SceneElement, Agent, Spawner, Timer, ...
    Entity can belong to one or multiple teams.
    """

    def __init__(
        self,
        name: Optional[str] = None,
        teams: Optional[Teams] = None,
        temporary: bool = False,
        **_,
    ):

        # Unique identifiers
        self._uid = None
        self._name = name

        # Teams
        if isinstance(teams, str):
            teams = [teams]
        elif not teams:
            teams = []

        self._teams = teams

        self._temporary = temporary

        self._removed = False

        self._playground = None

    @property
    def uid(self):
        return self._uid

    @uid.setter
    def uid(self, uid: int):
        self._uid = uid

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, name: str):
        self._name = name

    @property
    def teams(self):
        return self._teams

    @property
    def removed(self):
        return self._removed

    @removed.setter
    def removed(self, rem: bool):
        self._removed = rem

    @property
    def temporary(self):
        return self._temporary

    @property
    def playground(self):
        return self._playground

    @playground.setter
    def playground(self, playground: Optional[Playground]):
        self._playground = playground

    @property
    def rng(self):

        if self._playground:
            return self._playground.rng

        return None

    # Interactions with playground

    def reset(self):
        """
        Upon reset of the Playgroung,
        revert the entity back to its original state.
        """

    def pre_step(self):
        """
        Preliminary calculations before the pymunk engine steps.
        """

    def post_step(self):
        """
        Updates the entity state after pymunk engine steps.
        """

    def update_team_filter(self):
        pass
