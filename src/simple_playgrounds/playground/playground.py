""" Contains the base class for Playgrounds.

Playground class should be inherited to create environments
where agents can play.
Playground defines the physics and mechanics of the game, and manages
how entities interact with each other.

Examples can be found in :
    - simple_playgrounds/playgrounds/empty.py
    - simple_playgrounds/playgrounds/collection
"""
from __future__ import annotations
from abc import ABC, abstractmethod
from typing import Tuple, Union, List, Dict, Optional, Type, TYPE_CHECKING

import pymunk, pygame

if TYPE_CHECKING:
    from simple_playgrounds.common.position_utils import InitCoord

from simple_playgrounds.common.definitions import PYMUNK_STEPS

from simple_playgrounds.playground.collision_handlers import (gem_activates_element,
                                                              agent_activates_element,
                                                              agent_touches_element,
                                                              agent_grasps_element,
                                                              agent_teleports,
                                                              modifier_modifies_device
                                                              )

from simple_playgrounds.common.definitions import SPACE_DAMPING, CollisionTypes, PymunkCollisionCategories
from simple_playgrounds.agent.agent import Agent
from simple_playgrounds.entity.entity import Entity, EmbodiedEntity
from simple_playgrounds.entity.physical import PhysicalEntity
from simple_playgrounds.entity.interactive import StandAloneInteractive


# pylint: disable=unused-argument
# pylint: disable=line-too-long


class Playground(ABC):
    """ Playground is a Base Class that manages the physical simulation.

    Playground manages the interactions between Agents and Scene Elements.

    Attributes:
        initial_agent_coordinates: position or PositionAreaSampler,
            Starting position of an agent (single agent).
        done: bool, True if the playground reached termination.

    Notes:
          In the case of multi-agent setting, individual initial positions can be defined when
          instantiating the playground.
    """

    # pylint: disable=too-many-instance-attributes

    time_limit = None
    time_limit_reached_reward = None

    def __init__(
        self,
    ):

        # By default, size is infinite and center is at (0,0)
        self._size = None
        self._center = (0, 0)

        # Initialization of the pymunk space, modelling all the physics
        self.space = self._initialize_space()

        # Public attributes for entities in the playground
        self._entities: List[Entity] = []

        # Private attributes for managing interactions in playground
        self._disappeared_entities: List[Entity] = []

        # Timers to handle periodic events
        self.done = False
        self.initial_agent_coordinates: Optional[InitCoord] = None

        self._handle_interactions()
        self._timestep = 0

        self._shapes_to_entities: Dict[pymunk.Shape, Entity] = {}

        self._teams = {}

    @staticmethod
    def _initialize_space() -> pymunk.Space:
        """ Method to initialize Pymunk empty space for 2D physics.

        Returns: Pymunk Space

        """
        space = pymunk.Space()
        space.gravity = pymunk.Vec2d(0., 0.)
        space.damping = SPACE_DAMPING

        return space

    @property
    def size(self):
        return self._size

    @property
    def center(self):
        return self._center

    @property
    def timestep(self):
        return self._timestep

    @property
    def teams(self):
        return self._teams

    @property
    def _physical_entities(self):
        return [ent for ent in self._entities if isinstance(ent, PhysicalEntity)]

    @property
    def _agents(self):
        return [ent for ent in self._entities if isinstance(ent, Agent)]

    def add_team(self, team):
        assert team not in self._teams
        team_index = len(PymunkCollisionCategories) + len(self._teams) + 1
        self._teams[team] = team_index

    def update_teams(self):
        for entity in self._entities:
            entity.update_team_filter()

    def update(self, pymunk_steps: Optional[int] = PYMUNK_STEPS):
        """ Update the Playground

        Updates the Playground.
        Time moves by one unit of time.

        Args:
            pymunk_steps: Number of steps for the pymunk physics engine to run.

        Notes:
            pymunk_steps only influences the micro-steps that the physical engine is taking to render
            the movement of objects and collisions.
            From an external point of view, one unit of time passes independent on the number
            of pymunk_steps.

        """

        for entity in self._entities:
            entity.pre_step()

        for _ in range(pymunk_steps):
            self.space.step(1. / pymunk_steps)

        for entity in self._entities:
            entity.update()

        self._timestep += 1

    def reset(self):
        """
        Reset the Playground to its initial state.
        """

        # remove physical entities from playground to replace them later.
        for entity in self._physical_entities:
            if entity.held_by:
                entity.held_by.release_grasp()

            self.remove(entity)

            if not entity.temporary:
                self._disappeared_entities.append(entity)

        # reset entities that are non physical
        for entity in self._entities:
            entity.reset()

        # replace physical entities in the playground
        for entity in self._disappeared_entities.copy():
            self.add(entity)
            entity.reset()

        self._timestep = 0
        self.done = False

    def add(self,
            entity: Entity,
            initial_coordinates: Optional[InitCoord] = None,
            **kwargs,
            ):

        self._entities.append(entity)
        entity.add_to_playground(self, initial_coordinates=initial_coordinates, **kwargs)

    def remove(self,
               entity: EmbodiedEntity,
               definitive: Optional[bool] = False,
               ):

        self._entities.remove(entity)
        entity.remove_from_playground()

        if not definitive and not entity.temporary:
            self._disappeared_entities.append(entity)

    @abstractmethod
    def within_playground(self, coordinates):
        ...

    def get_closest_agent(self, entity: EmbodiedEntity) -> Agent:
        return min(self._agents,
                   key=lambda a: entity.position.get_dist_sqrd(a.position))

    def get_entity_from_shape(self, shape: pymunk.Shape):
        assert shape in self._shapes_to_entities.keys()
        return self._shapes_to_entities[shape]

    def view(self,
             center: Tuple[float, float],
             size: Tuple[float, float],
             invisible_elements: Optional[Union[List[Entity],
                                                Entity]] = None,
             draw_invisible: bool = False,
             surface: Optional[pygame.Surface] = None,
    ):

        if not surface:
            surface = pygame.Surface(size)

        else:
            assert surface.get_size() == size

        center = (center[0] - size[0]/2, center[1] - size[1]/2)

        surface.fill(pygame.Color(0, 0, 0))

        max_range = pymunk.Vec2d(*size).length

        shapes_in_range = self.space.point_query(center,
                                                 max_range,
                                                 shape_filter=pymunk.ShapeFilter(pymunk.ShapeFilter.ALL_MASKS()))

        elems = set([self._shapes_to_entities[shape.shape] for shape in shapes_in_range])

        # First, draw Interactives
        elems_interactive = [elem for elem in elems if not isinstance(elem, StandAloneInteractive)]
        elems_physical = [elem for elem in elems if not isinstance(elem, PhysicalEntity)]

        if not invisible_elements:
            invisible_elements = []

        for elem in elems_interactive + elems_physical:
            if elem not in invisible_elements:
                elem.draw(surface, viewpoint=center, draw_transparent=draw_invisible)

        img = pygame.surfarray.pixels3d(surface).astype(float)[:, :, ::-1]

        return img

    def _handle_interactions(self):

        # Order is important

        self.add_interaction(CollisionTypes.PART, CollisionTypes.GRASPABLE,
                             agent_grasps_element)
        self.add_interaction(CollisionTypes.PART, CollisionTypes.CONTACT,
                             agent_touches_element)
        self.add_interaction(CollisionTypes.PART, CollisionTypes.ACTIVABLE,
                             agent_activates_element)
        self.add_interaction(CollisionTypes.GEM,
                             CollisionTypes.ACTIVABLE_BY_GEM,
                             gem_activates_element)
        self.add_interaction(CollisionTypes.PART, CollisionTypes.TELEPORT,
                             agent_teleports)
        self.add_interaction(CollisionTypes.MODIFIER, CollisionTypes.DEVICE,
                             modifier_modifies_device)

    def add_interaction(
        self,
        collision_type_1: CollisionTypes,
        collision_type_2: CollisionTypes,
        interaction_function,
    ):
        """

        Args:
            collision_type_1: collision type of the first entity
            collision_type_2: collision type of the second entity
            interaction_function: function that handles the interaction

        Returns: None

        """

        handler = self.space.add_collision_handler(collision_type_1,
                                                   collision_type_2)
        handler.pre_solve = interaction_function
        handler.data['playground'] = self


class PlaygroundRegister:
    """
    Class to register Playgrounds.
    """

    playgrounds: Dict[str, Dict[str, Type[Playground]]] = {}

    @classmethod
    def register(
        cls,
        playground_group: str,
        playground_name: str,
    ):
        """
        Registers a playground
        """
        def decorator(subclass):

            if playground_group not in cls.playgrounds:
                cls.playgrounds[playground_group] = {}

            if playground_name in cls.playgrounds[playground_group]:
                raise ValueError(playground_name + ' already registered')

            cls.playgrounds[playground_group][playground_name] = subclass
            return subclass

        return decorator


class EmptyPlayground(Playground):

    def within_playground(self, coordinates):
        return True
