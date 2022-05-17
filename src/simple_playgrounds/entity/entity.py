""" Contains the base class for entities.

Entity classes should be used to create body parts of
an agent, scene entities, spawners, timers, etc.

Entity is the generic building block of physical and interactive
objects in simple-playgrounds.

"""
from __future__ import annotations
from abc import ABC, abstractmethod
from typing import List, Optional, TYPE_CHECKING, Union


if TYPE_CHECKING:
    from simple_playgrounds.playground.playground import Playground

Teams = Union[str, List[str]]


class Entity(ABC):
    """
    Base class that defines the entities that composing a Playground.
    Entities can be: SceneElement, Agent, Spawner, Timer, ...
    Entity can belong to one or multiple teams.
    """

    def __init__(self, 
                 playground: Playground,
                 name: Optional[str] = None,
                 teams: Optional[Teams] = None):

        self._playground = playground

        self._uid, self._name = self._playground._get_uid_name(self, name)

        self._teams: List[str] = self._add_to_teams(teams)
        
        self._playground.add_to_mappings(self)

        self._removed = False

    @property
    def uid(self):
        return self._uid

    @property
    def name(self):
        return self._name

    @property
    def teams(self):
        return self._teams

    @property
    def removed(self):
        return self._removed

    def _add_to_teams(self, teams: Optional[Teams] = None):

        if not teams:
            return []

        if isinstance(teams, str):
            teams = [teams]

        for team in teams:
            self._playground.add_team(team)

        return teams

    @abstractmethod
    def remove(self, definitive: bool=False):

        if definitive:
            self._playground.remove_from_mappings(entity=self)
   
        self._removed = True

    @abstractmethod
    def reset(self, **_):
        """
        Upon reset of the Playgroung,
        revert the entity back to its original state.
        """

    @abstractmethod
    def pre_step(self, **_):
        """
        Preliminary calculations before the pymunk engine steps.
        """
        ...

    @abstractmethod
    def post_step(self, **_):
        """
        Updates the entity state after pymunk engine steps.
        """
        ...

    @abstractmethod
    def update_team_filter(self, **_):
        pass
