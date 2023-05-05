from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Dict, List, Optional, Tuple, Union

import gymnasium
import pymunk
import pymunk.matplotlib_util
from gymnasium import spaces
from gymnasium.core import ActType

from spg.playground.actions import zero_action_space
from spg.position import Coordinate, CoordinateSampler
from .mixin import SpaceManager, ViewManager
from ..entity import Agent, Element, Entity

if TYPE_CHECKING:
    from ..entity.mixin.interaction import BarrierMixin


class Playground(gymnasium.Env, SpaceManager, ViewManager, ABC):
    def __init__(self, size: Tuple[int, int], **kwargs) -> None:

        self.size = size
        self.width, self.height = self.size

        ViewManager.__init__(self, **kwargs)
        SpaceManager.__init__(self, **kwargs)

        self.reset()

    @abstractmethod
    def place_elements(self) -> List[Element]:
        pass

    @abstractmethod
    def place_agents(self) -> List[Agent]:
        pass

    ###############
    # Entities
    ###############

    @property
    def action_space(self):
        return spaces.Dict({agent.name: agent.action_space for agent in self.agents})

    @property
    def null_action(self):
        return zero_action_space(self)

    @property
    def observation_space(self):
        return spaces.Dict(
            {agent.name: agent.observation_space for agent in self.agents}
        )

    ###############
    # STEP
    ###############

    def step(self, action: ActType):
        """Update the Playground

        Updates the Playground.
        Time moves by one unit of time.

        Args:
            action: The action to be performed by the agents. Dict of spaces.Space

        """

        self._pre_step()

        for agent_name, agent_action in action.items():
            agent = self.name_to_agents[agent_name]
            agent.apply_action(agent_action)

        self.pymunk_step()

        self._post_step()

        observation = self._compute_observation()
        reward = self._compute_reward()

        return observation, reward, self._terminated, False, {}

    def _pre_step(self):

        for element in self.elements:
            element.pre_step()

        for agent in self.agents:
            agent.pre_step()

    def _post_step(self):

        for element in self.elements:
            element.post_step()

        for agent in self.agents:
            agent.post_step()

    def _compute_observation(self):

        # self.update_sensor_view()

        obs = {}
        # for agent in self.agents:
        #     obs[agent.name] = agent.observation

        return obs

    def _compute_reward(self):
        return {agent: agent.reward for agent in self.agents}

    def reset(self):
        """
        Reset the Playground to its initial state.
        """

        # Initialization of the pymunk space, modelling all the physics
        self.initialize_space()

        for view in self.views:
            view.reset()

        # Mappings
        self.shapes_to_entities: Dict[pymunk.Shape, Entity] = {}
        self.name_to_agents: Dict[str, Agent] = {}
        self.uids_to_entities: Dict[int, Entity] = {}

        self.elements: List[Element] = []
        self.agents: List[Agent] = []
        self.barriers: List[BarrierMixin] = []

        # Lists containing elements in the playground
        self.place_elements()
        self.place_agents()

        self._terminated = False

        obs = self._compute_observation()

        return obs, {}

    # ADD REMOVE ENTITIES
    def get_uid(self):

        while True:
            uid = self.np_random.integers(0, 2**24)
            if uid not in self.uids_to_entities:
                return uid

    def add(
        self,
        entity: Entity,
        coordinate: Optional[Union[Coordinate, CoordinateSampler]] = None,
        allow_overlapping=True,
    ):

        entity.playground = self
        entity.uid = self.get_uid()

        if not entity.name:
            entity.name = f"{entity.__class__.__name__}_{entity.uid}"

        if entity.name in self.name_to_agents:
            raise ValueError(f"Agent {entity.name} already exists in the playground")

        if isinstance(entity, Element):
            self.elements.append(entity)

        elif isinstance(entity, Agent):
            self.agents.append(entity)
            self.name_to_agents[entity.name] = entity

        self.shapes_to_entities.update({shape: entity for shape in entity.pm_shapes})
        self.uids_to_entities[entity.uid] = entity

        # Add to the views
        for view in self.views:
            view.add(entity)

        # Add to space:
        if entity.pm_body is not None:
            self.space.add(entity.pm_body)
        self.space.add(*entity.pm_shapes)

        for attached_entity in entity.attached:
            self.add(attached_entity)

        # Once all attachements have been added, we can move the entity and fix the attachements
        if isinstance(entity, (Agent, Element)):
            assert coordinate is not None
            entity.move_to(coordinate, allow_overlapping)
            entity.fix_attached()

    def remove(self, entity):

        if isinstance(entity, Agent):
            self.agents.remove(entity)
            self.name_to_agents.pop(entity.name)

        if isinstance(entity, Element):
            self.elements.remove(entity)

        self.uids_to_entities.pop(entity.uid)

        if entity.pm_body is not None:
            self.space.remove(entity.pm_body)

        self.space.remove(*entity.pm_shapes)

        for attached_entity in entity.attached:
            self.remove(attached_entity)

            if hasattr(entity, 'joint') and entity.joint is not None:
                self.space.remove(attached_entity.joint)

            if hasattr(entity, 'motor') and entity.motor is not None:
                self.space.remove(attached_entity.motor)

            if hasattr(entity, 'limit') and entity.limit is not None:
                self.space.remove(attached_entity.limit)

        for view in self.views:
            view.remove(entity)

    def within_playground(
        self,
        entity: Entity,
    ):

        if isinstance(entity, (Agent, Element)):
            for attached_entity in entity.attached:
                if not self.within_playground(attached_entity):
                    return False

        return self.coordinates_is_valid(entity.coordinates)

    def coordinates_is_valid(self, coordinate: Coordinate) -> bool:

        position = coordinate[0]

        if not -self.width / 2 <= position[1] <= self.width / 2:
            return False

        if not -self.height / 2 <= position[1] <= self.height / 2:
            return False

        return True

    def get_closest_agent(self, entity: Entity) -> Agent:
        return min(self.agents, key=lambda a: entity.position.get_dist_sqrd(a.position))


class EmptyPlayground(Playground):
    def place_agents(self):
        pass

    def place_elements(self):
        pass
