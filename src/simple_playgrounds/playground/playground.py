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
import gc

from abc import abstractmethod
from typing import List, Dict, Optional, Type, Union, Tuple, TYPE_CHECKING

from PIL.Image import init
from arcade import Window
from simple_playgrounds import playground
from simple_playgrounds.agent.part import interactives
from simple_playgrounds.common.position_utils import Coordinate
from simple_playgrounds.element.element import SceneElement

from simple_playgrounds.entity.physical import PhysicalEntity

if TYPE_CHECKING:
    from simple_playgrounds.common.gui import GUI

import pymunk
import numpy as np

import matplotlib.pyplot as plt
import pymunk.matplotlib_util

from simple_playgrounds.entity.interactive import (
    AnchoredInteractive,
)


from simple_playgrounds.common.definitions import PYMUNK_STEPS


from simple_playgrounds.common.definitions import (
    SPACE_DAMPING,
    CollisionTypes,
    PymunkCollisionCategories,
)
from simple_playgrounds.agent.agent import Agent
from simple_playgrounds.entity.embodied import EmbodiedEntity
from simple_playgrounds.entity.entity import Entity

from simple_playgrounds.agent.part.part import (
    AnchoredPart,
    InteractivePart,
    PhysicalPart,
)
from simple_playgrounds.agent.part.controller import Controller, Command
from simple_playgrounds.agent.device.communication import CommunicationDevice, Message

from simple_playgrounds.agent.device.sensor import Sensor, SensorValue

from simple_playgrounds.playground.collision_handlers import grasper_grasps_graspable

# pylint: disable=unused-argument
# pylint: disable=line-too-long

CommandsDict = Dict[Agent, Dict[Controller, Command]]
SentMessagesDict = Dict[Agent, Dict[CommunicationDevice, Message]]

ObservationsDict = Dict[Agent, Dict[Sensor, SensorValue]]
ReceivedMessagesDict = Dict[Agent, Dict[CommunicationDevice, Message]]
RewardsDict = Dict[Agent, float]

# arcade.Window
# super().__init__(1, 1, visible=False, antialiasing=True)  # type: ignore
# self.ctx.blend_func = self.ctx.ONE, self.ctx.ZERO


class Playground:
    """Playground is a Base Class that manages the physical simulation.

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
        size: Optional[Tuple[int, int]] = None,
        seed: Optional[int] = None,
        background: Optional[
            Union[Tuple[int, int, int], List[int], Tuple[int, int, int, int]]
        ] = None,
    ):

        # Random number generator for replication, rewind, etc.
        self._rng = np.random.default_rng(seed)

        # By default, size is infinite and center is at (0,0)
        self._center = (0, 0)
        self._size = size
        if size:
            self._width, self._height = size
        else:
            self._width = self._height = None

        # Background color
        if not background:
            background = (0, 0, 0, 0)

        self._background = background

        # Initialization of the pymunk space, modelling all the physics
        self._space = self._initialize_space()

        # Lists containing entities in the playground
        self._entities: List[EmbodiedEntity] = []
        self._agents: List[Agent] = []
        self._teams = {}

        # Private attributes for managing interactions in playground
        self._done: bool = False
        self._timestep: int = 0

        # Mappings
        self._shapes_to_entities: Dict[pymunk.Shape, EmbodiedEntity] = {}
        self._name_to_agents: Dict[str, Agent] = {}
        self._uids_to_entities: Dict[int, EmbodiedEntity] = {}

        self._handle_interactions()
        self._views = []

        # Arcade window necessary to create contexts, views, sensors and gui
        self._window = Window(1, 1, visible=False, antialiasing=True)  # type: ignore
        self._window.ctx.blend_func = self._window.ctx.ONE, self._window.ctx.ZERO

    def debug_draw(self, plt_width, center=None, size=None):

        if not center:
            center = self._center

        if not size:
            if not self._size:
                raise ValueError("Size must be set for display")
            size = self._size

        fig_size = (plt_width, plt_width / size[0] * size[1])

        fig = plt.figure(figsize=fig_size)

        ax = plt.axes(
            xlim=(center[0] - size[0] / 2, center[0] + size[0] / 2),
            ylim=(center[1] - size[1] / 2, center[1] + size[1] / 2),
        )
        ax.set_aspect("equal")

        options = pymunk.matplotlib_util.DrawOptions(ax)
        options.collision_point_color = (10, 20, 30, 40)
        self._space.debug_draw(options)
        # ax.invert_yaxis()
        plt.show()
        del fig

    @property
    def window(self):
        return self._window

    @property
    def initial_agent_coordinates(self):
        return (0, 0), 0

    @property
    def background(self):
        return self._background

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
        """Method to initialize Pymunk empty space for 2D physics.

        Returns: Pymunk Space

        """
        space = pymunk.Space()
        space.gravity = pymunk.Vec2d(0.0, 0.0)
        space.damping = SPACE_DAMPING

        return space

    ###############
    # Entities
    ###############

    def _get_identifier(self, entity: Entity):

        uid = None
        background = (
            self._background[0]
            + self._background[1] * 256
            + self._background[2] * 256 * 256
        )

        while True:
            a = self._rng.integers(0, 2**24)

            if a not in self._uids_to_entities and a != background:
                uid = a
                break

        name = entity.name
        if not name:
            name = type(entity).__name__ + "_" + str(uid)

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

        team_index = len(PymunkCollisionCategories) + len(self._teams) + 1
        self._teams[team] = team_index

    def _update_all_team_filters(self):

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
        pymunk_steps: int = PYMUNK_STEPS,
    ):
        """Update the Playground

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
            self.space.step(1.0 / pymunk_steps)

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

            if entity.temporary:
                self.remove(entity, definitive=True)

            else:

                entity.reset()

                if isinstance(entity, EmbodiedEntity):

                    if entity.removed:
                        self._add_to_space(
                            entity,
                            entity.initial_coordinates,
                            allow_overlapping=entity.allow_overlapping,
                        )
                        self._add_to_views(entity)
                    else:
                        entity.move_to(
                            entity.initial_coordinates,
                            allow_overlapping=entity.allow_overlapping,
                            keep_velocity=False,
                        )

        for agent in self._agents:
            agent.reset()

            if agent.removed:

                self._add_to_space(
                    agent, agent.initial_coordinates, agent.allow_overlapping
                )
                self._add_to_views(agent)

            else:
                agent.move_to(
                    agent.initial_coordinates,
                    allow_overlapping=agent.allow_overlapping,
                    keep_velocity=False,
                )

        # for view in self._views.copy():

        # self._views.remove(view)
        # self.add_view(view)

        self._timestep = 0
        self._done = False

        obs = self._compute_observations(**kwargs)
        rew = self._compute_rewards(**kwargs)

        return obs, rew, self.done

    # ADD REMOVE ENTITIES

    def add(self, entity, initial_coordinates=None, allow_overlapping=True):

        if isinstance(entity, Agent) and not initial_coordinates:
            initial_coordinates = self.initial_agent_coordinates

        if not initial_coordinates and self._size:
            initial_coordinates = (self._rng.random(2) - 0.5) * self._size

        if not initial_coordinates:
            raise ValueError(
                "Either initial coordinate or size of the environment should be set"
            )

        self._add_to_mappings(entity)
        self._add_to_space(entity, initial_coordinates, allow_overlapping)
        self._add_to_views(entity)
        self._update_teams(entity)

    def _add_to_mappings(self, entity):

        entity.playground = self
        entity.uid, entity.name = self._get_identifier(entity)

        self._uids_to_entities[entity.uid] = entity

        if isinstance(entity, Agent):
            self._agents.append(entity)
            self._name_to_agents[entity.name] = entity

            for part in entity.parts:
                self._add_to_mappings(part)

        elif not isinstance(entity, (AnchoredInteractive, PhysicalPart)):
            self._entities.append(entity)

        if not isinstance(entity, Agent):
            for pm_shape in entity.pm_shapes:
                self._shapes_to_entities[pm_shape] = entity

        if isinstance(entity, PhysicalEntity):
            for interactive in entity.interactives:
                self._add_to_mappings(interactive)

    def _add_to_space(self, entity, initial_coordinates, allow_overlapping):

        entity.removed = False

        if isinstance(entity, Agent):

            entity.initial_coordinates = initial_coordinates
            entity.allow_overlapping = allow_overlapping

            for part in entity.parts:
                self._add_to_space(part, initial_coordinates, allow_overlapping)

        elif isinstance(entity, AnchoredInteractive):
            self._space.add(*entity.pm_shapes)

        else:

            if isinstance(entity, AnchoredPart):
                initial_coordinates = entity.get_init_coordinates()

            entity.initial_coordinates = initial_coordinates
            entity.allow_overlapping = allow_overlapping
            self._space.add(*entity.pm_elements)
            entity.move_to(initial_coordinates, allow_overlapping=allow_overlapping)

            if isinstance(entity, AnchoredPart):
                entity.attach_to_anchor()
                self._space.add(*entity.pm_joints)

            if isinstance(entity, PhysicalEntity) and not isinstance(
                entity, PhysicalPart
            ):
                for interactive in entity.interactives:
                    self._add_to_space(
                        interactive, initial_coordinates, allow_overlapping=True
                    )

    def _add_to_views(self, entity):

        if isinstance(entity, Agent):
            for part in entity.parts:
                self._add_to_views(part)
            return

        for view in self._views:
            view.add(entity)

    def _update_teams(self, entity):
        new_team = False
        for team in entity.teams:
            if team not in self._teams.keys():
                self.add_team(team)
                new_team = True

        if new_team:
            self._update_all_team_filters()
        else:
            entity.update_team_filter()

    def remove(self, entity, definitive=False):

        self._remove_from_space(entity)
        self._remove_from_views(entity)

        if definitive:
            self._remove_from_mappings(entity)

    def _remove_from_space(self, entity):

        entity.removed = True

        if isinstance(entity, Agent):
            for part in entity.parts:
                self._remove_from_space(part)
        else:
            self._space.remove(*entity.pm_elements)

            if isinstance(entity, AnchoredPart):
                self._space.remove(*entity.pm_joints)

        if isinstance(entity, PhysicalEntity) and not isinstance(entity, PhysicalPart):
            for interactive in entity.interactives:
                self._remove_from_space(interactive)

    def _remove_from_mappings(self, entity):

        self._uids_to_entities.pop(entity.uid)

        if isinstance(entity, Agent):
            self._agents.remove(entity)

            assert entity.name
            self._name_to_agents.pop(entity.name)

            for part in entity.parts:
                self._remove_from_mappings(part)

        elif not isinstance(entity, (AnchoredInteractive, PhysicalPart)):
            self._entities.remove(entity)

        if not isinstance(entity, Agent):
            for pm_shape in entity.pm_shapes:
                self._shapes_to_entities.pop(pm_shape)

        if isinstance(entity, PhysicalEntity) and not isinstance(entity, PhysicalPart):
            for interactive in entity.interactives:
                self._remove_from_mappings(interactive)

        entity.playground = None

    def _remove_from_views(self, entity):

        if isinstance(entity, Agent):
            for part in entity.parts:
                self._remove_from_views(part)
            return

        for view in self._views:
            view.remove(entity)

    def add_view(self, view):

        for entity in self.entities:
            view.add(entity)

        for agent in self.agents:
            view.add(agent.base)

        self._views.append(view)

    def within_playground(
        self,
        entity: Optional[Union[Agent, EmbodiedEntity]] = None,
        coordinates: Optional[Coordinate] = None,
    ):

        if not self._size:
            return True

        if isinstance(entity, Agent):
            for part in entity.parts:
                if not self.within_playground(part):
                    return False

        if entity:
            position = entity.position
        elif coordinates:
            position = coordinates[0]
        else:
            raise ValueError("entity or coordinates must be specified")

        if not -self._size[0] / 2 <= position[0] <= self._size[0] / 2:
            return False

        if not -self._size[1] / 2 <= position[1] <= self._size[1] / 2:
            return False

        return True

    def overlaps(self, entity: EmbodiedEntity, coordinates):
        """Tests whether new coordinate would lead to physical collision"""

        dummy_body = pymunk.Body(body_type=pymunk.Body.STATIC)
        dummy_shapes = []
        for pm_shape in entity.pm_shapes:
            dummy_shape = pm_shape.copy()
            dummy_shape.body = dummy_body
            dummy_shape.sensor = True
            dummy_shapes.append(dummy_shape)

        self.space.add(dummy_body, *dummy_shapes)

        dummy_body.position, dummy_body.angle = coordinates
        self.space.reindex_static()

        overlaps = []
        for dummy_shape in dummy_shapes:
            overlaps += self.space.shape_query(dummy_shape)
        self.space.remove(dummy_body, *dummy_shapes)

        # remove sensor shapes
        overlaps = [
            elem
            for elem in overlaps
            if elem.shape
            and not elem.shape.sensor
            and elem.shape not in entity.pm_shapes
        ]

        self.space.reindex_static()

        return bool(overlaps)

    def get_closest_agent(self, entity: EmbodiedEntity) -> Agent:
        return min(self.agents, key=lambda a: entity.position.get_dist_sqrd(a.position))

    def get_entity_from_shape(self, shape: pymunk.Shape):
        assert shape in self._shapes_to_entities.keys()

        entity = self._shapes_to_entities[shape]

        return entity

    def _handle_interactions(self):

        # Order is important

        self.add_interaction(
            CollisionTypes.GRASPER, CollisionTypes.GRASPABLE, grasper_grasps_graspable
        )

        # self.add_interaction(CollisionTypes.PART, CollisionTypes.CONTACT,

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

        handler = self.space.add_collision_handler(collision_type_1, collision_type_2)
        handler.pre_solve = interaction_function
        handler.data["playground"] = self

    # def __del__(self):
    #     self.close()
    #     # gc.collect()
    #     super().__del__()


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
                raise ValueError(playground_name + " already registered")

            cls.playgrounds[playground_group][playground_name] = subclass
            return subclass

        return decorator
