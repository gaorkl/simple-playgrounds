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
from typing import List, Dict, Optional, Type, TYPE_CHECKING, Union

import pymunk
import numpy as np
import pickle

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
from simple_playgrounds.agent.actuators import ActuatorDevice
from simple_playgrounds.device.sensors.semantic import Detection
from simple_playgrounds.device.sensor import SensorDevice

from simple_playgrounds.device.communication import Stream

# pylint: disable=unused-argument
# pylint: disable=line-too-long

Timestep = int
ScalarReward = int
Message = Union[np.ndarray, str]

AgentIdentifier = Union[str, Agent]
ActuatorIdentifier = Union[str, ActuatorDevice]
SensorIdentifier = Union[str, SensorDevice]

Action = Union[float, Message]
AgentAction = Union[
    Dict[ActuatorIdentifier, Action ],
    np.ndarray]
ActionDict = Dict[AgentIdentifier, AgentAction]

Observation = Union[np.ndarray, List[Detection], Message]
AgentObservation = Union[
    Dict[SensorIdentifier, Observation],
    np.ndarray]
ObservationDict = Dict[AgentIdentifier, AgentObservation]

RewardDict = Dict[AgentIdentifier, ScalarReward]


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
        seed: Optional[int] = None,
    ):

        # Random number generator for replication, rewind, etc.
        self._rng = np.random.default_rng(seed)

        # Checkpoints for easy rewind
        self._checkpoints: Dict[Timestep, bytes] = {}
        self._actions: Dict[Timestep, ActionDict] = {}

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
        self._timestep: Timestep = 0

        self._shapes_to_entities: Dict[pymunk.Shape, Entity] = {}

        self._teams = {}

        # Save Initial Checkpoint
        self._initial_checkpoint = self._get_checkpoint()
        self._checkpoints[0] = self._initial_checkpoint

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

    def step(
        self,
        actions: Optional[ActionDict] = None,
        **kwargs,
    ):

        actions = self._apply_actions(actions)
        self._save_actions_for_replay(actions)

        self._update_playground(**kwargs)

        obs = self._compute_observations(**kwargs)
        rew = self._compute_rewards(**kwargs)

        return obs, rew, self.done

    def _apply_actions(self, actions: ActionDict) -> ActionDict:

        action_dict : ActionDict = {}

        for agent in self._agents:

            if agent in actions:
                agent.set_actions(actions[agent])

            elif agent.name in actions:
                agent.set_actions(actions[agent.name])

            else:
                agent.set_actions()

            action_dict[agent] = agent.actuator_action_dict

        return action_dict

    def _save_actions_for_replay(self,
                                 actions,
                                 save_messages: Optional[bool] = False,
                                 **kwargs):

        actions_str = {}
        for agent, actuator_dict in actions.items():
            actions_str[agent.name] = {}

            for actuator, command in actuator_dict.items():
                actions_str[agent.name][actuator.name] = command

        self._actions[self._timestep] = command

    def _compute_observations(self,
                              compute_observations: Optional[bool] = True,
                              keys_are_str: Optional[bool] = False,
                              return_np_arrays: Optional[bool] = False,
                              **kwargs):

        obs = {}
        if not compute_observations:
            return obs

        for agent in self._agents:

            if keys_are_str:
                key_ = agent.name
            else:
                key_ = agent

            agent.compute_observations()

            if return_np_arrays:
                obs[key_] = agent.np_observations
            else:
                obs[key_] = agent.observations



    def save_checkpoint(self):
        # noinspection PyTypeChecker
        self._checkpoints[self._timestep] = self._get_checkpoint()

    def delete_checkpoints(self, timestep: int):
        if timestep == 0:
            raise ValueError('Can not remove initial checkpoint')
        self._checkpoints.remove = { 0: self._init_checkpoint }

    def _get_checkpoint(self):
        pg = copy.copy(self)
        return pickle.dumps(pg)

    def _update_playground(self, pymunk_steps: Optional[int] = PYMUNK_STEPS):
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

        # Save Initial Checkpoint
        self._initial_checkpoint = self._get_checkpoint()
        self._checkpoints[0] = self._initial_checkpoint

    def add(self,
            entity: Entity,
            initial_coordinates: Optional[InitCoord] = None,
            **kwargs,
            ):

        if isinstance(entity, EmbodiedEntity):
            self.add_to_mappings(entity)

        entity.add_to_playground(self, initial_coordinates=initial_coordinates, **kwargs)

    def add_to_mappings(self, entity):
        self._entities.append(entity)
        self._shapes_to_entities[entity.pm_shape] = entity

    def remove(self,
               entity: EmbodiedEntity,
               definitive: Optional[bool] = False,
               ):

        self.remove_from_mappings(entity)
        entity.remove_from_playground()

        if not definitive and not entity.temporary:
            self._disappeared_entities.append(entity)

    def remove_from_mappings(self, entity):
        self._entities.remove(entity)
        self._shapes_to_entities.pop(entity.pm_shape)

    @abstractmethod
    def within_playground(self, coordinates):
        ...

    def get_closest_agent(self, entity: EmbodiedEntity) -> Agent:
        return min(self._agents,
                   key=lambda a: entity.position.get_dist_sqrd(a.position))

    def get_entity_from_shape(self, shape: pymunk.Shape):
        assert shape in self._shapes_to_entities.keys()
        return self._shapes_to_entities[shape]

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
