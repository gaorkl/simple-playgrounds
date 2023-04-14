""" Contains the base class for Playgrounds.

Playground class should be inherited to create environments
where agents can play.
Playground defines the physics and mechanics of the game, and manages
how elements interact with each other.

Examples can be found in :
    - spg/playgrounds/empty.py
    - spg/playgrounds/collection
"""
# pylint: disable=too-many-public-methods

from __future__ import annotations

from typing import Dict, List, Optional, Tuple, Type, Union

import matplotlib.pyplot as plt
import numpy as np
import pymunk
import pymunk.matplotlib_util
from arcade import Window

from gymnasium import spaces
from gymnasium.core import ActType


from spg.element.element import PhysicalElement, SceneElement

from ..agent import Agent
from ..agent.device.communicator import Communicator, Message
from ..agent.part import AnchoredPart, PhysicalPart
from ..agent.device.sensor import RayCompute, RaySensor, Sensor, SensorValue
from ..entity import EmbodiedEntity, Entity, InteractiveAnchored
from ..utils.definitions import (
    PYMUNK_STEPS,
    SPACE_DAMPING,
    CollisionTypes,
    PymunkCollisionCategories,
)
from ..utils.position import Coordinate
from .collision_handlers import disabler_disables_device, grasper_grasps_graspable

# pylint: disable=unused-argument
# pylint: disable=line-too-long

TargetCommunicator = Optional[Union[Communicator, List[Communicator]]]
SentMessagesDict = Dict[Agent, Dict[Communicator, Tuple[TargetCommunicator, Message]]]

ObservationsDict = Dict[Agent, Dict[Sensor, SensorValue]]
ReceivedMessagesDict = Dict[Agent, Dict[Communicator, Tuple[Communicator, Message]]]
RewardsDict = Dict[Agent, float]


class Playground:
    """Playground is a Base Class that manages the physical simulation.

    Playground manages the interactions between Agents and Scene Elements.

    Attributes:
        initial_agent_coordinates: position or PositionAreaSampler,
            Starting position of an agent (single agent).
        done: bool, True if the playground reached termination.

    Notes:
          In the case of multi-agent setting,
          individual initial positions can be defined when
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
        use_shaders=True,
    ):

        # Random number generator for replication, rewind, etc.
        self._rng = np.random.default_rng(seed)

        # By default, size is infinite and center is at (0,0)
        self._center = (0, 0)
        self._size = size
        self._width: Optional[int]
        self._height: Optional[int]

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

        # Lists containing elements in the playground
        self._elements: List[SceneElement] = []
        self._agents: List[Agent] = []
        self._teams = {}

        # Private attributes for managing interactions in playground
        self._done: bool = False
        self._timestep: int = 0

        # Mappings
        self._shapes_to_entities: Dict[pymunk.Shape, EmbodiedEntity] = {}
        self._name_to_agents: Dict[str, Agent] = {}
        self._uids_to_entities: Dict[int, Entity] = {}

        self._handle_interactions()
        self._views = []

        # Arcade window necessary to create contexts, views, sensors and gui
        self._window = Window(1, 1, visible=False, antialiasing=True)  # type: ignore
        self._window.ctx.blend_func = self._window.ctx.ONE, self._window.ctx.ZERO

        self._ray_compute = None
        self._use_shaders = use_shaders

        self.pymunk_steps = PYMUNK_STEPS

    def debug_draw(self, plt_width=10, center=None, size=None):

        # todo: replace magic number by size calculation
        # depending on object position (boundingbox)

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
    def ray_compute(self):

        if not self._ray_compute:
            assert self._size
            self._ray_compute = RayCompute(
                self, self._size, self._center, zoom=1, use_shader=self._use_shaders
            )

        return self._ray_compute

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

    def _get_uid(self, entity: Entity):

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

        return uid

    def get_entity_from_uid(self, uid):

        return self._uids_to_entities[uid]

    @property
    def agents(self):
        return [agent for agent in self._agents if not agent.removed]

    @property
    def elements(self):
        return [elem for elem in self._elements if not elem.removed]

    @property
    def action_space(self):
        return spaces.Dict({agent.name: agent.action_space for agent in self.agents})


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

        for element in self._elements:
            element.update_team_filter()

        for agent in self._agents:
            agent.update_team_filter()

    ###############
    # STEP
    ###############

    def step(self, action: ActType):
        """Update the Playground

        Updates the Playground.
        Time moves by one unit of time.

        Args:
            pymunk_steps: Number of steps for the pymunk physics engine to run.

        Notes:
            the physical engine is taking to render
            the movement of objects and collisions.
            From an external point of view,
            one unit of time passes independent on the number
            of pymunk_steps.

        """

        obs, mess, rew = None, None, None

        self._pre_step()

        if not self._done:

            for agent_name, agent_action in action.items():
                agent = self._name_to_agents[agent_name]
                agent.apply_action(agent_action)

            for _ in range(PYMUNK_STEPS):
                self.space.step(1.0 / PYMUNK_STEPS)

            self._post_step()
            self._done = self._has_terminated()

            obs = self._compute_observations()
            rew = {agent: agent.reward for agent in self._agents}
            # if messages:
            #     mess = self._transmit_messages(messages)

            self._timestep += 1

        return obs, mess, rew, self._done

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

    def _transmit_messages(self, messages):

        msgs = {agent: {} for agent in self.agents}

        all_sent_messages = [
            (agent, comm_source, target)
            for agent, comms_dict in messages.items()
            for comm_source, target in comms_dict.items()
        ]

        for agent, comm_source, target in all_sent_messages:

            assert comm_source.agent is agent

            comm_target, message = target
            msg = comm_source.send(message)

            if not msg:
                continue

            if isinstance(comm_target, list):

                for targ in comm_target:
                    assert isinstance(targ, Communicator)
                    received_msg = targ.receive(comm_source, msg)

                    if received_msg:
                        msgs[targ.agent][targ] = (comm_source, received_msg)

            elif isinstance(comm_target, Communicator):
                received_msg = comm_target.receive(comm_source, msg)

                if received_msg:
                    msgs[comm_target.agent][comm_target] = (comm_source, received_msg)

            elif comm_target is None:
                for agent in self.agents:
                    for comm in agent.communicators:
                        received_msg = comm.receive(comm_source, msg)
                        if received_msg:
                            msgs[comm.agent][comm] = (comm_source, received_msg)

            else:
                raise ValueError

        return msgs

    def _compute_observations(self):

        if self._ray_compute:
            self._ray_compute.update_sensors()

        obs = {}
        for agent in self.agents:
            obs[agent] = agent.compute_observations()

        return obs

    def _has_terminated(self):
        return False

    def reset(self):
        """
        Reset the Playground to its initial state.
        """
        # reset elements that are still in playground
        for element in self._elements:

            if element.temporary:
                self.remove(element, definitive=True)
            elif element.removed:
                self.add(element, from_removed=True)
            elif isinstance(element, PhysicalElement) and element.movable:
                assert element.initial_coordinates
                element.move_to(
                    element.initial_coordinates,
                    element.allow_overlapping,
                )
            elif isinstance(element, EmbodiedEntity) and element.moved:
                assert element.initial_coordinates
                element.move_to(
                    element.initial_coordinates,
                    element.allow_overlapping,
                )

            element.reset()

        for agent in self._agents:
            agent.reset()
            if agent.removed:
                self.add(agent, from_removed=True)
            else:
                agent.base.move_to(
                    agent.initial_coordinates,
                    allow_overlapping=agent.allow_overlapping,
                    move_anchors=True,
                )

        for view in self._views:
            view.update(force=True)

        self._timestep = 0
        self._done = False

        obs = self._compute_observations()

        return obs, None, None, self._done

    # ADD REMOVE ENTITIES

    def add(
        self,
        entity,
        initial_coordinates=None,
        allow_overlapping=True,
        from_removed=False,
    ):

        entity.playground = self

        if from_removed:
            initial_coordinates = entity.initial_coordinates
            allow_overlapping = entity.allow_overlapping

        self._add_to_space(entity, initial_coordinates, allow_overlapping)

        if not from_removed:
            self._add_to_mappings(entity)

        self._add_to_views(entity)

        if isinstance(entity, Agent):
            self.add(
                entity.base,
                initial_coordinates=initial_coordinates,
                allow_overlapping=allow_overlapping,
                from_removed=from_removed,
            )

        if isinstance(entity, PhysicalPart):

            for part in entity.anchored:
                self.add(
                    part, allow_overlapping=allow_overlapping, from_removed=from_removed
                )

            for device in entity.devices.values():
                self.add(
                    device,
                    allow_overlapping=allow_overlapping,
                    from_removed=from_removed,
                )

                if isinstance(device, RaySensor):
                    self.ray_compute.add(device)

        elif isinstance(entity, PhysicalElement):
            for interactive in entity.interactives:
                self.add(
                    interactive,
                    allow_overlapping=allow_overlapping,
                    from_removed=from_removed,
                )

        self._update_teams(entity)

    def _add_to_space(self, entity, initial_coordinates, allow_overlapping):

        entity.removed = False

        if isinstance(entity, InteractiveAnchored):
            self._space.add(*entity.pm_shapes)
            return

        if isinstance(entity, AnchoredPart):
            initial_coordinates = entity.get_init_coordinates()

        elif isinstance(entity, Agent) and not initial_coordinates:
            initial_coordinates = self.initial_agent_coordinates

        elif entity.initial_coordinates:
            initial_coordinates = entity.initial_coordinates

        if not initial_coordinates:
            raise ValueError(
                "Either initial coordinate or size of the environment should be set"
            )

        entity.initial_coordinates = initial_coordinates
        entity.allow_overlapping = allow_overlapping

        if isinstance(entity, Agent):
            return

        self._space.add(*entity.pm_elements)
        entity.move_to(
            initial_coordinates,
            allow_overlapping=allow_overlapping,
        )

        if isinstance(entity, AnchoredPart):
            entity.attach_to_anchor()
            self._space.add(*entity.pm_joints)

    def _add_to_mappings(self, entity):

        entity.uid = self._get_uid(entity)
        self._uids_to_entities[entity.uid] = entity

        if isinstance(entity, Agent):
            self._agents.append(entity)
            self._name_to_agents[entity.name] = entity

        elif isinstance(entity, SceneElement):
            self._elements.append(entity)

        if isinstance(entity, EmbodiedEntity):
            for pm_shape in entity.pm_shapes:
                self._shapes_to_entities[pm_shape] = entity

    def _add_to_views(self, entity):

        if isinstance(entity, Agent):
            return

        for view in self._views:
            view.add(entity)

    def _update_teams(self, entity):

        if not isinstance(entity, (SceneElement, Agent)):
            return

        new_team = False
        for team in entity.teams:
            if team not in self._teams:
                self.add_team(team)
                new_team = True

        if new_team:
            self._update_all_team_filters()

        entity.update_team_filter()

    def remove(self, entity, definitive=False):

        self._remove_from_space(entity)
        self._remove_from_views(entity)

        if definitive:
            self._remove_from_mappings(entity)

        if isinstance(entity, Agent):
            self.remove(entity.base, definitive)

        if isinstance(entity, PhysicalPart):
            for part in entity.anchored:
                self.remove(part, definitive)

            for device in entity.devices:
                self.remove(device, definitive)

        elif isinstance(entity, PhysicalElement):

            for interactive in entity.interactives:
                self.remove(interactive, definitive)

            for grasper in entity.grasped_by:
                grasper.release(entity)

        entity.removed = True

    def _remove_from_space(self, entity):

        if isinstance(entity, Agent):
            return

        self._space.remove(*entity.pm_elements)

        if isinstance(entity, AnchoredPart):
            self._space.remove(*entity.pm_joints)

    def _remove_from_mappings(self, entity):

        assert entity.uid

        self._uids_to_entities.pop(entity.uid)

        if isinstance(entity, Agent):
            self._agents.remove(entity)

            assert entity.name
            self._name_to_agents.pop(entity.name)

        elif isinstance(entity, SceneElement):
            self._elements.remove(entity)

        if not isinstance(entity, Agent):
            for pm_shape in entity.pm_shapes:
                self._shapes_to_entities.pop(pm_shape)

        entity.playground = None

    def _remove_from_views(self, entity):

        if isinstance(entity, Agent):
            return
        for view in self._views:
            view.remove(entity)

    def add_view(self, view):

        for entity in self.elements:
            view.add(entity)

            if isinstance(entity, PhysicalElement):
                for interactive in entity.interactives:
                    view.add(interactive)

        for agent in self.agents:
            for part in agent.parts:
                view.add(part)

                for device in part.devices:
                    view.add(device)

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

        if isinstance(entity, PhysicalPart):
            agent_shapes = []
            for part in entity.agent.parts.values():
                agent_shapes += part.pm_shapes

            overlaps = [elem for elem in overlaps if elem.shape not in agent_shapes]

        self.space.reindex_static()

        return bool(overlaps)

    def get_closest_agent(self, entity: EmbodiedEntity) -> Agent:
        return min(self.agents, key=lambda a: entity.position.get_dist_sqrd(a.position))

    def get_entity_from_shape(self, shape: pymunk.Shape):
        assert shape in self._shapes_to_entities

        entity = self._shapes_to_entities[shape]

        return entity

    def _handle_interactions(self):

        # Order is important

        self.add_interaction(
            CollisionTypes.GRASPER, CollisionTypes.GRASPABLE, grasper_grasps_graspable
        )

        self.add_interaction(
            CollisionTypes.DISABLER, CollisionTypes.DEVICE, disabler_disables_device
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
