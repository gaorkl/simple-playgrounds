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

import copy
from abc import ABC, abstractmethod
from typing import List, Dict, Optional, Type, TYPE_CHECKING, Union, Tuple

import pymunk
import numpy as np

from simple_playgrounds.entity.embodied.interactive import AnchoredInteractive, InteractiveEntity, StandAloneInteractive


from simple_playgrounds.common.definitions import PYMUNK_STEPS

# from simple_playgrounds.playground.collision_handlers import (gem_activates_element,
#                                                               agent_activates_element,
#                                                               agent_touches_element,
#                                                               agent_grasps_element,
#                                                               agent_teleports,
#                                                               modifier_modifies_device
#                                                               )

from simple_playgrounds.common.definitions import SPACE_DAMPING, CollisionTypes, PymunkCollisionCategories
from simple_playgrounds.agent.agent import Agent
from simple_playgrounds.entity.entity import Entity
from simple_playgrounds.entity.embodied.embodied import EmbodiedEntity

from simple_playgrounds.agent.part.part import Part
from simple_playgrounds.agent.controller import Controller, Command
from simple_playgrounds.agent.communication import Receiver, Transmitter, Message

from simple_playgrounds.agent.sensor.sensor import Sensor, SensorValue

# pylint: disable=unused-argument
# pylint: disable=line-too-long

CommandsDict = Dict[Agent, Dict[Controller, Command]]
SentMessagesDict = Dict[Agent, Dict[Transmitter, Message]]

ObservationsDict = Dict[Agent, Dict[Sensor, SensorValue]]
ReceivedMessagesDict = Dict[Agent, Dict[Receiver, Message]]
RewardsDict = Dict[Agent, float]


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

          Always reset the playground before starting a run.

    """

    # pylint: disable=too-many-instance-attributes

    time_limit = None
    time_limit_reached_reward = None

    def __init__(
        self,
        seed: Optional[int] = None,
    ):

        # Random number generator for replication, rewind, etc.
        self._rng = np.random.default_rng(seed)

        # By default, size is infinite and center is at (0,0)
        self._size = None
        self._center = (0, 0)

        # Initialization of the pymunk space, modelling all the physics
        self._space = self._initialize_space()

        # Lists containing entities in the playground
        self._entities: List[Entity] = []
        self._agents: List[Agent] = []
        self._teams = {}

        # Private attributes for managing interactions in playground
        self._done: bool = False
        self._timestep: int = 0

        # Mappings
        self._shapes_to_entities: Dict[pymunk.Shape, Entity] = {}
        self._name_to_agents: Dict[str, Agent] = {}
        self._uids_to_entities: Dict[int, Entity] = {}

        # self._handle_interactions()

    @property
    def rng(self):
        return self._rng

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
    def done(self):
        return self._done


    #################
    # Pymunk space
    #################

    @property
    def space(self):
        return self._space

    @staticmethod
    def _initialize_space() -> pymunk.Space:
        """ Method to initialize Pymunk empty space for 2D physics.

        Returns: Pymunk Space

        """
        space = pymunk.Space()
        space.gravity = pymunk.Vec2d(0., 0.)
        space.damping = SPACE_DAMPING

        return space

    ###############
    # Entities
    ###############

    def _get_uid_name(self, entity: Entity, name: Optional[str] = None):
 
        while True:
            a = self._rng.integers(0, 2**24)
            if a not in self._uids_to_entities:
                uid = a
                break

        if not name:
            name = type(entity).__name__ + '_' + str(id)
        
        if name in [ent.name for ent in self.entities]:
            raise ValueError("Entity with this name already in Playground")

        return uid, name
   
    @property
    def agents(self):
        return [agent for agent in self._agents if not agent.removed]

    @property
    def entities(self):
        return [ent for ent in self._entities if not ent.removed]
  
    ###########
    # TEAMS
    ###########

    @property
    def teams(self):
        return self._teams
 
    def add_team(self, team):
        
        if not team in self._teams.keys():
            team_index = len(PymunkCollisionCategories) + len(self._teams) + 1
            self._teams[team] = team_index

        self._update_team_filter()

    def _update_team_filter(self):

        for entity in self._entities:
            entity.update_team_filter()

        for agent in self._agents:
            agent.update_team_filter()

    
    ###############
    # STEP
    ###############

    def step(
        self,
        commands: Optional[CommandsDict] = None,
        messages: Optional[SentMessagesDict] = None,
        skip_state_compute: bool = False,
        pymunk_steps: int = PYMUNK_STEP
    ):
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

        self._pre_step()
        self._apply_commands(commands)

        for _ in range(pymunk_steps):
            self.space.step(1. / pymunk_steps)

        self._post_step()
        
        if not skip_state_compute:
            obs = self._compute_observations()
            rew = self._compute_rewards()
            mess = self._transmit_messages(messages)
        else:
            obs, mess, rew = None, None, None

        self._timestep += 1
        
        return obs, mess, rew, self._done

    def _pre_step(self):

        for entity in self.entities:
            entity.pre_step()

        for agent in self.agents:
            agent.pre_step()
    
    def _post_step(self):

        for entity in self.entities:
            entity.post_step()

        for agent in self.agents:
            agent.post_step()


    def _apply_commands(self, commands):

        if not commands:
            return

        for agent, command_dict in commands.items():
            agent.receive_commands(command_dict)
  
        for agent in self._agents:
            agent.apply_commands()

    def _transmit_messages(self, messages):
        
        if not messages:
            return



    def _compute_observations(self):

        obs = {}
        for agent in self.agents:
             obs[agent] = agent.compute_observations()

        return obs

    def _compute_rewards(self):

        rew = {}
        for agent in self.agents:
            rew[agent] = agent.compute_rewards()
        
        return rew

    def reset(self, **kwargs):
        """
        Reset the Playground to its initial state.
        """

        # reset entities that are still in playground
        for entity in self._entities:
            entity.reset()
        
        for agent in self._agents:
            agent.reset()

        self._timestep = 0
        self._done = False

        obs = self._compute_observations(**kwargs)
        rew = self._compute_rewards(**kwargs)

        return obs, rew, self.done

    def add_to_mappings(self, entity):

        self._uids_to_entities[entity.uid] = entity
        
        if isinstance(entity, Agent):
            self._agents.append(entity)
            self._name_to_agents[entity.name] = entity

        elif not isinstance(entity, (AnchoredInteractive, Part)):
            self._entities.append(entity)

        if not isinstance(entity, Agent):
            self._shapes_to_entities[entity.pm_shape] = entity

    def remove_from_mappings(self, entity):

        self._uids_to_entities.pop(entity.uid)

        if isinstance(entity, Agent):
            self._agents.remove(entity)
            self._name_to_agents.pop(entity.name)

        elif not isinstance(entity, (AnchoredInteractive, Part)):
            self._entities.remove(entity)

        if not isinstance(entity, Agent):
            self._shapes_to_entities.pop(entity.pm_shape)

    @abstractmethod
    def within_playground(self, coordinates):
        ...


    def overlaps(self, entity: EmbodiedEntity, coordinates):
        """ Tests whether new coordinate would lead to physical collision """

        dummy_body = pymunk.Body(body_type=pymunk.Body.STATIC)
        dummy_shape = entity.pm_shape.copy()
        dummy_shape.body = dummy_body
        dummy_shape.sensor = True
       
        self.space.add(dummy_shape.body, dummy_shape)

        dummy_shape.body.position, dummy_shape.body.angle = coordinates
        self.space.reindex_static()

        overlaps = self.space.shape_query(dummy_shape)
        self.space.remove(dummy_shape.body, dummy_shape)

        # remove sensor shapes
        overlaps = [elem for elem in overlaps 
                    if elem.shape and not elem.shape.sensor 
                    and elem.shape is not entity.pm_shape]

        self.space.reindex_static()

        return bool(overlaps)


    def get_closest_agent(self, entity: EmbodiedEntity) -> Agent:
        return min(self.agents,
                   key=lambda a: entity.position.get_dist_sqrd(a.position))

    def get_entity_from_shape(self, shape: pymunk.Shape):
        assert shape in self._shapes_to_entities.keys()
        
        entity = self._shapes_to_entities[shape]

        return entity
        


#     def _handle_interactions(self):

#         # Order is important

#         self.add_interaction(CollisionTypes.PART, CollisionTypes.GRASPABLE,
#                              agent_grasps_element)
#         self.add_interaction(CollisionTypes.PART, CollisionTypes.CONTACT,
#                              agent_touches_element)
#         self.add_interaction(CollisionTypes.PART, CollisionTypes.ACTIVABLE,
#                              agent_activates_element)
#         self.add_interaction(CollisionTypes.GEM,
#                              CollisionTypes.ACTIVABLE_BY_GEM,
#                              gem_activates_element)
#         self.add_interaction(CollisionTypes.PART, CollisionTypes.TELEPORT,
#                              agent_teleports)
#         self.add_interaction(CollisionTypes.MODIFIER, CollisionTypes.DEVICE,
#                              modifier_modifies_device)

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

    @property
    def initial_agent_coordinates(self):
        return (0, 0), 0

    def within_playground(self, coordinates):
        return True

    @property
    @abstractmethod
    def initial_agent_coordinates(self):
        ...


