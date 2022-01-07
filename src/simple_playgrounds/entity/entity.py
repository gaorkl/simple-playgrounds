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

    @property
    def playground(self):
        return self._playground

    @property
    def rng(self):
        return self._playground.rng

    @property
    def name(self):
        return self._name

    def _add_to_teams(self, teams: List[Any] = [], **kwargs):

        for team in teams:

            self._teams.append(team)
            if team not in self._playground.teams.keys():
                self._playground.add_team(team)
                self._playground.update_team_filter()

    def remove(self, definitive: bool = True):

        self._remove_from_pymunk_space()
        
        if disappear


    @abstractmethod
    def remove_from_pymunk_space(self):
        """
        Remove pymunk elements from playground space.
        Remove entity from lists or dicts in playground.
        """

    @abstractmethod
    def update_team_filter(self):
        """
        Apply mask filter to the shape of interest of the entity.
        """
        ...

    @abstractmethod
    def pre_step(self, **kwargs):
        """
        Preliminary calculations before the pymunk engine steps.
        """
        ...

    @abstractmethod
    def post_step(self, **kwargs):
        """
        Updates the entity state after pymunk engine steps.
        """
        ...

    @abstractmethod
    def reset(self, **kwargs):
        """
        Upon reset of the Playgroung,
        revert the entity back to its original state.
        """
        ...
