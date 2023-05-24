from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Dict, List, Optional, Tuple, Union

import gymnasium
import pymunk
import pymunk.matplotlib_util
from gymnasium import spaces
from gymnasium.core import ActType
from matplotlib import pyplot as plt

from spg.core.entity.communication import CommunicationMixin
from spg.core.playground.utils import zero_action_space
from spg.core.position import Coordinate, CoordinateSampler

from ..entity import Agent, Element, Entity
from ..entity.sensor import SensorMixin
from .manager import SpaceManager, ViewManager
from .manager.collision import CollisionManager
from .manager.communication import CommunicationManager
from .manager.sensor import SensorManager

if TYPE_CHECKING:
    from spg.components.elements.barrier import BarrierMixin


class Playground(
    gymnasium.Env,
    SpaceManager,
    ViewManager,
    CollisionManager,
    CommunicationManager,
    SensorManager,
    ABC,
):
    def __init__(self, size: Tuple[int, int], **kwargs) -> None:

        self.size = size
        self.width, self.height = self.size

        self.elements: List[Element] = []
        self.agents: List[Agent] = []

        ViewManager.__init__(self, **kwargs)
        SpaceManager.__init__(self, **kwargs)
        CollisionManager.__init__(self, **kwargs)
        CommunicationManager.__init__(self, **kwargs)
        SensorManager.__init__(self, **kwargs)

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
        return spaces.Dict(
            {agent.name: agent.agent_action_space for agent in self.agents}
        )

    @property
    def null_action(self):
        return zero_action_space(self)

    @property
    def observation_space(self):
        return spaces.Dict(
            {agent.name: agent.agent_observation_space for agent in self.agents}
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
            agent.agent_apply_action(agent_action)

        self.pymunk_step()

        self._post_step()

        observation = self._compute_observation()
        reward = self._compute_reward()

        return observation, reward, self._terminated, False, {}

    def _pre_step(self):

        for view in self.views:
            view.updated = False

        for element in self.elements:
            element.pre_step()

        for agent in self.agents:
            agent.pre_step()

        self.clear_messages()

    def _post_step(self):

        for element in self.elements:
            element.post_step()

        for agent in self.agents:
            agent.post_step()

    def _compute_observation(self):

        self.update_sensors()

        obs = {}
        for agent in self.agents:
            obs[agent.name] = agent.agent_observation

        return obs

    def _compute_reward(self):
        return {agent: agent.reward for agent in self.agents}

    def reset(self):
        """
        Reset the Playground to its initial state.
        """

        # Initialization of the pymunk space, modelling all the physics
        self.initialize_space()
        self.add_interactions()

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

            if entity.name in self.name_to_agents:
                raise ValueError(
                    f"Agent {entity.name} already exists in the playground"
                )

            self.name_to_agents[entity.name] = entity

        self.shapes_to_entities.update({shape: entity for shape in entity.pm_shapes})
        self.uids_to_entities[entity.uid] = entity

        # Add to space:
        if entity.pm_body is not None:
            self.space.add(entity.pm_body)
        self.space.add(*entity.pm_shapes)

        for attached_entity in entity.attached:
            self.add(attached_entity)

        if isinstance(entity, SensorMixin):
            self.add_sensor(entity)

        # Once all attachements have been added, we can move the entity and fix the attachements
        if isinstance(entity, (Agent, Element)):
            assert coordinate is not None
            entity.move_to(coordinate, allow_overlapping)
            entity.fix_attached()

            # Add to the views
            for view in self.views:
                view.add(entity)

        if isinstance(entity, CommunicationMixin):
            entity.subscribe_to_topics()

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

            if hasattr(attached_entity, "joint") and attached_entity.joint is not None:
                self.space.remove(attached_entity.joint)

            if hasattr(attached_entity, "motor") and attached_entity.motor is not None:
                self.space.remove(attached_entity.motor)

            if hasattr(attached_entity, "limit") and attached_entity.limit is not None:
                self.space.remove(attached_entity.limit)

        if isinstance(entity, (Agent, Element)):
            for view in self.views:
                view.remove(entity)

        if isinstance(entity, CommunicationMixin):
            entity.unsubscribe_from_topics()

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

    def draw(self, plt_width=10, center=None, size=None):

        if not center:
            center = (0, 0)

        if not size:
            size = self.size

        fig_size = (plt_width, plt_width / size[0] * size[1])

        fig = plt.figure(figsize=fig_size)

        ax = plt.axes(
            xlim=(center[0] - size[0] / 2, center[0] + size[0] / 2),
            ylim=(center[1] - size[1] / 2, center[1] + size[1] / 2),
        )
        ax.set_aspect("equal")

        options = pymunk.matplotlib_util.DrawOptions(ax)
        options.collision_point_color = (10, 20, 30, 40)
        self.space.debug_draw(options)
        plt.show()
        del fig


class EmptyPlayground(Playground):
    def place_agents(self):
        pass

    def place_elements(self):
        pass
