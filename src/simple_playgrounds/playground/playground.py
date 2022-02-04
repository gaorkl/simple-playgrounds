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
from numpy.lib.arraysetops import isin

import pymunk
import numpy as np
import pickle

from simple_playgrounds.entity.embodied.interactive import AnchoredInteractive, InteractiveEntity, StandAloneInteractive

if TYPE_CHECKING:
    from simple_playgrounds.common.position_utils import InitCoord

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
from simple_playgrounds.entity.embodied.physical import PhysicalEntity

from simple_playgrounds.agent.part.part import Part
from simple_playgrounds.agent.controller import Controller, Command
from simple_playgrounds.agent.communication import Receiver, Transmitter, Message

from simple_playgrounds.common.definitions import Detection
from simple_playgrounds.agent.sensor.sensor import Sensor, SensorValue

# pylint: disable=unused-argument
# pylint: disable=line-too-long

Timestep = int
ScalarReward = float

AgentIdentifier = Union[str, Agent]
ControllerIdentifier = Union[str, Controller]
TransmitterIdentifier = Union[str, Transmitter]
SensorIdentifier = Union[str, Sensor]

Commands = Union[
    Dict[ControllerIdentifier, Command],
    np.ndarray]
AgentCommandsDict = Dict[AgentIdentifier, Commands]

Messages = Dict[TransmitterIdentifier, Message]
AgentMessagesDict = Dict[AgentIdentifier, Message]

SensorValues = Union[
    Dict[SensorIdentifier, SensorValue],
    np.ndarray]

ReceivedMessages = Dict[AgentIdentifier, Messages]

Rewards = Dict[AgentIdentifier, ScalarReward]


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

        # Checkpoints for easy rewind
        self._checkpoints: Dict[Timestep, bytes] = {}
        self._actions: Dict[Timestep, Tuple[AgentCommandsDict, AgentMessagesDict]] = {}

        # By default, size is infinite and center is at (0,0)
        self._size = None
        self._center = (0, 0)

        # Initialization of the pymunk space, modelling all the physics
        self.space = self._initialize_space()

        # Lists containing entities in the playground
        self._entities: List[Entity] = []
        self._agents: List[Agent] = []
        self._teams = {}

        # Private attributes for managing interactions in playground
        self._done: bool = False
        self._timestep: Timestep = 0

        # Mappings
        self._shapes_to_entities: Dict[pymunk.Shape, Entity] = {}
        self._entity_name_count: Dict[type, int] = {}
        self._name_to_agents: Dict[str, Agent] = {}

        # self._handle_interactions()

    @staticmethod
    def _initialize_space() -> pymunk.Space:
        """ Method to initialize Pymunk empty space for 2D physics.

        Returns: Pymunk Space

        """
        space = pymunk.Space()
        space.gravity = pymunk.Vec2d(0., 0.)
        space.damping = SPACE_DAMPING

        return space

    ##################
    # Playground
    ##################

    @property
    @abstractmethod
    def initial_agent_coordinates(self):
        ...

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

    ###############
    # Entities
    ###############

    @property
    def teams(self):
        return self._teams
    
    @property
    def agents(self):
        return [agent for agent in self._agents if not agent.removed]

    @property
    def entities(self):
        return [ent for ent in self._entities if not ent.removed]

    @property
    def physical_entities(self):
        return [ent for ent in self.entities if isinstance(ent, PhysicalEntity)]

    @property
    def interactive_entities(self):
        return [ent for ent in self.entities if isinstance(ent, InteractiveEntity)]

    def add_team(self, team):
        
        if not team in self._teams.keys():
            team_index = len(PymunkCollisionCategories) + len(self._teams) + 1
            self._teams[team] = team_index

        self._update_team_filter()

    def get_name(self, entity: Entity):
        index = self._entity_name_count.get(type(entity), 0)
        self._entity_name_count[type(entity)] = index + 1
        name = type(entity).__name__ + '_' + str(index)
        return name

    def _update_team_filter(self):

        for entity in self._entities:
            entity.update_team_filter()

        for agent in self._agents:
            agent.update_team_filter()


    def step(
        self,
        commands: Optional[AgentCommandsDict] = None,
        messages: Optional[AgentMessagesDict] = None,
        **kwargs,
    ):

        self._save_actions_for_replay(commands, messages)
        self._pre_step()
        
        self._apply_commands(commands)
        self._transmit_messages(messages)

        self._update_playground(**kwargs)

        obs = self._compute_observations(**kwargs)
        rew = self._compute_rewards(**kwargs)

        return obs, rew, self._done

    def _pre_step(self):

        for entity in self.entities:
            entity.pre_step()

        for agent in self.agents:
            agent.pre_step()


    def _apply_commands(self, commands):

        if commands:
            for agent, _commands in commands.items():

                if isinstance(agent, str):
                    agent = self._name_to_agents[agent]

                agent.receive_commands(_commands)
  
        for agent in self._agents:
            agent.apply_commands()

    def _transmit_messages(self, messages):
        pass

    def _update_playground(self, pymunk_steps: int = PYMUNK_STEPS, **_):
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

        for _ in range(pymunk_steps):
            self.space.step(1. / pymunk_steps)

        for entity in self.entities:
            entity.post_step()

        for agent in self.agents:
            agent.post_step()

        self._timestep += 1


    def _compute_observations(self,
                              compute_observations: Optional[bool] = True,
                              keys_are_str: Optional[bool] = False,
                              return_np_arrays: Optional[bool] = False,
                              **_):

        obs = {}
        if not compute_observations:
            return obs

        for agent in self.agents:

            if keys_are_str:
                key_ = agent.name
            else:
                key_ = agent

            obs[key_] = agent.compute_observations(keys_are_str, return_np_arrays)

    def _compute_rewards(self,
                         compute_observations: Optional[bool] = True,
                         keys_are_str: Optional[bool] = False,
                         return_np_arrays: Optional[bool] = False,
                         **_):

        obs = {}
        if not compute_observations:
            return obs

        for agent in self.agents:

            if keys_are_str:
                key_ = agent.name
            else:
                key_ = agent

            obs[key_] = agent.compute_observations(keys_are_str, return_np_arrays)

    ################
    # Checkpoints
    ################

    def save_checkpoint(self):
        self._checkpoints[self._timestep] = self._get_checkpoint()

    def delete_checkpoints(self):
        self._checkpoints = {}

    def _get_checkpoint(self):
        pg = copy.copy(self)
        pg._checkpoints = {}
        return pickle.dumps(pg)

 
    def _save_actions_for_replay(self, commands, messages):
        self._actions[self._timestep] = commands, messages

   
    def rewind(self, timesteps_rewind, random_alternate: bool = False, **kwargs):

        # load pg
        valid_checkpoints = [ts for ts in self._checkpoints.keys() if ts <= self._timestep - timesteps_rewind]
        if not valid_checkpoints:
            raise ValueError('no checkpoints were saved for rewind')

        ts_checkpoint = max(valid_checkpoints)
        pg = pickle.loads(self._checkpoints[ts_checkpoint])

        # Save before overriding playground
        future_actions = [self._actions[ts] for ts in range(ts_checkpoint, self._timestep-timesteps_rewind)]
        rng = self._rng
        checkpoints = self._checkpoints

        # Time travel
        self.__dict__.update(pg.__dict__)
        if random_alternate:
            self._rng = np.random.default_rng(seed=rng.integers(1000))

        # Apply all action between checkpoint and rewind point
        for act in future_actions:
            self.step(actions=act, compute_observations=False)

        self._checkpoints = {ts: checkpoint for ts, checkpoint in checkpoints.items() if ts <= self._timestep}
        self._actions = {ts: action for ts, action in self._actions.items() if ts <= self._timestep}

        obs = self._compute_observations(**kwargs)
        rew = self._compute_rewards(**kwargs)

        return obs, rew, self.done

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

    def add_to_mappings(self, entity, **_):

        if isinstance(entity, Agent):
            self._agents.append(entity)
            self._name_to_agents[entity.name] = entity

        elif not isinstance(entity, (AnchoredInteractive, Part)):
            self._entities.append(entity)

        if not isinstance(entity, Agent):
            self._shapes_to_entities[entity.pm_shape] = entity

    def remove_from_mappings(self, entity):

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
