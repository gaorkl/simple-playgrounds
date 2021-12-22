""" Contains the base class for entities.

Entity classes should be used to create body parts of
an agent, scene entities, spawners, timers, etc.

Entity is the generic building block of physical and interactive
objects in simple-playgrounds.

"""
from __future__ import annotations
from abc import ABC, abstractmethod
from typing import List, Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from simple_playgrounds.playground.playground import Playground


class Entity(ABC):
    """
    Base class that defines the entities that composing a Playground.
    Entities can be: SceneElement, Agent, Spawner, Timer, ...
    Entity can belong to one or multiple teams.
    """

    def __init__(self, name: Optional[str] = None, **kwargs):

        self._name: Optional[str] = name
        self._playground: Optional[Playground] = None
        self._teams: List[str] = []

    @property
    def playground(self):
        return self._playground

    @property
    def name(self):
        return self._name

    def add_to_playground(self, playground: Playground, **kwargs):
        if self._playground:
            assert self in playground.entities
            raise ValueError('Entity {} already in a Playground'.format(
                self._name))

        self._playground = playground

        # If in a team when added to the playground, add the team.
        for team in self._teams:
            if team not in self._playground.teams:
                self._playground.add_team(team)

        self._playground.update_teams()

        if not self._name:
            self._name = self._playground.get_name(self)

        # One new filters have been resolved, add to playground
        self._add_to_playground(**kwargs)

    @abstractmethod
    def _add_to_playground(self, **kwargs):
        """
        In the case of basic entities, Add pymunk elements to playground space.
        In the case of complex entities (e.g agents), add entities that compose
        this entity.

        Add entity to lists or dicts in playground.
        """
        ...

    def remove_from_playground(self):
        self._remove_from_playground()
        self._playground = None

    @abstractmethod
    def _remove_from_playground(self):
        """
        Remove pymunk elements from playground space.
        Remove entity from lists or dicts in playground.
        """

    def add_to_team(self, team):
        self._teams.append(team)

        # If already in playground, add the team
        if self._playground:

            if team not in self._playground.teams.keys():
                self._playground.add_team(team)

            self._playground.update_teams()

    def update_team_filter(self):
        pass

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
