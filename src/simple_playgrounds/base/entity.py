""" Contains the base class for entities.

Entity class should be used to create body parts of
an agent, or scene entities.
Entity is the generic building block of physical and interactive
objects in simple-playgrounds.

Examples can be found in :
    - simple_playgrounds/agents/parts
    - simple_playgrounds/playgrounds/scene_elements
"""

from abc import ABC, abstractmethod
from typing import Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from simple_playgrounds.playgrounds.playground import Playground


class Entity(ABC):
    """
    Base class that defines the interface between playground and entities that are composing it.
    Entities can be: SceneElement, Agent, Spawner, Timer, ...
    """

    index_entity = 0

    def __init__(self,
                 temporary: Optional[bool] = False,
                 name: Optional[str] = None):

        self._name: str

        if not name:
            name = self.__class__.__name__ + '_' + str(Entity.index_entity)
        self._name = name

        Entity.index_entity += 1

        self._playground: Optional[Playground] = None
        self._temporary = temporary

    @property
    def playground(self):
        return self._playground

    def add_to_playground(self, playground: Playground):
        if self._playground:
            raise ValueError('Entity {} already in a Playground'.format(self._name))

        self._playground = playground
        self._add_to_playground()

    @abstractmethod
    def _add_to_playground(self):
        ...

    def remove_from_playground(self):
        self._remove_from_playground()

    @abstractmethod
    def _remove_from_playground(self):
        ...

    @abstractmethod
    def pre_step(self):
        ...

    @abstractmethod
    def reset(self):
        ...

    @property
    def temporary(self):
        return self._temporary
