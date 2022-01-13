""" Contains the base class for entities.

Entity classes should be used to create body parts of
an agent, scene entities, spawners, timers, etc.

Entity is the generic building block of physical and interactive
objects in simple-playgrounds.

"""
from __future__ import annotations
from abc import ABC, abstractmethod
from typing import Any, List, Optional, TYPE_CHECKING, Union
import numpy as np

if TYPE_CHECKING:
    from simple_playgrounds.playground.playground import Playground


class Entity(ABC):
    """
    Base class that defines the entities that composing a Playground.
    Entities can be: SceneElement, Agent, Spawner, Timer, ...
    Entity can belong to one or multiple teams.
    """

    def __init__(self, 
                 playground: Playground,
                 name: Optional[str] = None,
                 **kwargs):

        self._playground = playground
        self._teams: List[str] = []

        self._name = name
        if not name:
            self._name = self._playground.get_name(self)
        
        self._add_to_teams(**kwargs)
        self._playground.add_to_mappings(self, **kwargs)

        self._removed = False 

    @property
    def playground(self):
        return self._playground

    @property
    def rng(self):
        return self._playground.rng

    @property
    def name(self):
        return self._name

    @property
    def teams(self):
        return self._teams

    @property
    def removed(self):
        return self._removed

    def _add_to_teams(self, teams: Optional[Union[str, List[str]]] = None, **_):

        if not teams:
            return

        if isinstance(teams, str):
            teams = [teams]

        for team in teams:
            self._teams.append(team)
            self._playground.add_team(team)
        
        self.update_team_filter()

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
    def update_team_filter(self):
        """
        Apply mask filter to the shape of interest of the entity.
        """
        ...

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


