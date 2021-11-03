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
from abc import ABC
from typing import Tuple, Union, List, Dict, Optional, Type, TYPE_CHECKING

import pymunk

if TYPE_CHECKING:
    from simple_playgrounds.device.communication import CommunicationDevice
    from simple_playgrounds.device.sensor import SensorDevice
    from simple_playgrounds.device.communication import CommunicationDevice
    from simple_playgrounds.agent.parts import Part
    from ..common.position_utils import InitCoord

from simple_playgrounds.common.definitions import PYMUNK_STEPS

from simple_playgrounds.playground.collision_handlers import (gem_activates_element,
                                                              agent_activates_element,
                                                              agent_touches_element,
                                                              agent_grasps_element,
                                                              agent_teleports,
                                                              modifier_modifies_device
                                                              )

from simple_playgrounds.common.definitions import SPACE_DAMPING, CollisionTypes, MAX_ATTEMPTS_OVERLAPPING
from simple_playgrounds.common.timer import Timer

from simple_playgrounds.element.element import SceneElement
from simple_playgrounds.agent.agent import Agent
from simple_playgrounds.agent.actuators import Grasp, Activate
from simple_playgrounds.common.spawner import Spawner
from simple_playgrounds.element.elements.activable import Dispenser

from simple_playgrounds.element.elements.modifier import ModifierElement
from simple_playgrounds.device.device import Device
from simple_playgrounds.element.element import InteractiveElement

from simple_playgrounds.element.elements.gem import GemElement
from simple_playgrounds.element.elements.teleport import TeleportElement


# pylint: disable=unused-argument
# pylint: disable=line-too-long


class Playground(ABC):
    """ Playground is a Base Class that manages the physical simulation.

    Playground manages the interactions between Agents and Scene Elements.

    Attributes:
        size: size of the scene (width, length).
        elements: list of SceneElements present in the Playground.
        spawners: list of spawners producing elements in the Playground.
        agents: list of Agents present in the Playground.
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
        size: Tuple[int, int],
    ):

        # Generate Scene
        assert isinstance(size, (tuple, list))
        assert len(size) == 2

        self.size = size
        self._width, self._length = self.size

        # Initialization of the pymunk space, modelling all the physics
        self.space = self._initialize_space()

        # Public attributes for entities in the playground
        self.elements: List[SceneElement] = []
        self.spawners: List[Spawner] = []
        self.agents: List[Agent] = []

        self.communication_devices: List[CommunicationDevice] = []
        self._sensor_devices: List[SensorDevice] = []

        # Private attributes for managing interactions in playground
        self._disappeared_elements: List[SceneElement] = []
        # self._grasped_elements: Dict[SceneElement, Grasp] = {}
        # self._teleported: List[Tuple[Agent, SceneElement]] = []

        # Timers to handle periodic events
        self._timers: Dict[Timer, InteractiveElement] = {}

        self.done = False
        self.initial_agent_coordinates: Optional[InitCoord] = None

        self._handle_interactions()
        self.sensor_collision_index = 2
        self._timestep = 0

    @staticmethod
    def _initialize_space() -> pymunk.Space:
        """ Method to initialize Pymunk empty space for 2D physics.

        Returns: Pymunk Space

        """
        space = pymunk.Space()
        space.gravity = pymunk.Vec2d(0., 0.)
        space.damping = SPACE_DAMPING

        return space

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

        self._spawners_produce()
        # self._check_teleports()

        for agent in self.agents:
            agent.pre_step()

        for elem in self.elements:
            elem.pre_step()
            if elem.trajectory:
                self.space.reindex_shapes_for_body(elem.pm_body)

        for comm in self.communication_devices:
            comm.pre_step()

        for sensor in self._sensor_devices:
            sensor.pre_step()

        self._update_timers()

        for _ in range(pymunk_steps):
            self.space.step(1. / pymunk_steps)

        self._timestep += 1

    @property
    def timestep(self):
        return self._timestep

    def reset(self):
        """
        Reset the Playground to its initial state.
        """

        # remove entities which are temporary. Reset the others
        for element in self.elements.copy():
            if element.held_by:
                element.held_by.release_grasp()

            if element.temporary:
                self._remove_element_from_playground(element)
            else:
                element.reset()
                self._move_to_initial_position(element)

        # reset and replace entities that are not temporary
        for element in self._disappeared_elements.copy():
            element.reset()
            self._add_element_to_playground(element)
            self._move_to_initial_position(element)

        # reset spawners
        for spawner in self.spawners:
            spawner.reset()

        # reset agents
        for agent in self.agents.copy():
            agent.reset()
            self._move_to_initial_position(agent)

        # reset timers
        for timer in self._timers:
            timer.reset()

        # reset communication devices
        for comm in self.communication_devices:
            comm.reset()

        # reset sensor devices
        # for sens in self._sensor_devices:
        #     sens.reset()

        self._timestep = 0
        self.done = False

    def add_agent(
        self,
        agent: Agent,
        initial_coordinates: Optional[InitCoord] = None,
        allow_overlapping: Optional[bool] = True,
        max_attempts: Optional[int] = MAX_ATTEMPTS_OVERLAPPING,
    ):
        """ Method to add an Agent to the Playground.

        Args:
            agent: Agent to add to the Playground
            initial_coordinates: tuple or CoordinateSampler
            allow_overlapping: If True, allows new agent to overlap with other elements when added to the Playground.
            max_attempts: If overlapping is not allowed, maximum number of attempts to place the agent.
        """

        assert isinstance(agent, Agent)

        # If already there
        if agent in self.agents:
            raise ValueError('Agent already in Playground')

        # Save overlapping strategy of agent.
        agent.overlapping_strategy = allow_overlapping, max_attempts

        # Set initial position. Either set or from playground.
        if initial_coordinates:
            agent.initial_coordinates = initial_coordinates
        elif self.initial_agent_coordinates:
            agent.initial_coordinates = self.initial_agent_coordinates
        else:
            raise ValueError(
                """Agent initial position should be defined in the playground or passed as an argument
                             to the class agent""")

        self._add_agent_to_playground(agent)
        self._add_sensor_devices(agent)
        self._add_communication_devices(agent)
        self._move_to_initial_position(agent)

        agent.playground = self

    def remove_agent(self, agent: Agent):
        """
        Removes an agent from a playground.

        Args:
            agent: Agent to remove.

        """

        assert agent in self.agents

        agent.reset()
        for part in agent.parts:
            self.space.remove(*part.pm_elements)

        if agent.communication:
            self.communication_devices.remove(agent.communication)
            self.space.remove(agent.communication.pm_shape)

        for sensor in agent.sensors:
            self._sensor_devices.remove(sensor)
            self.space.remove(sensor.pm_shape)

        self.agents.remove(agent)
        agent.playground = None
        assert not agent.in_playground

    def add_spawner(self, spawner: Spawner):

        assert isinstance(spawner, Spawner)

        # If already there
        if spawner in self.spawners:
            raise ValueError('Spawner already in Playground')

        self.spawners.append(spawner)
        spawner.playground = self

    def add_element(
        self,
        element: SceneElement,
        initial_coordinates: Optional[InitCoord] = None,
        allow_overlapping: Optional[bool] = True,
        max_attempts: Optional[int] = MAX_ATTEMPTS_OVERLAPPING,
    ):
        """ Method to add a SceneElement to the Playground.

        Args:
            element: Scene Element to add to the Playground
            initial_coordinates: initial position and angle of the SceneElement.
                Can be list [x,y,theta], AreaPositionSampler or Trajectory.
            allow_overlapping: If True, allows new elements to overlap with other elements when added to the Playground.
            max_attempts: If overlapping is not allowed, maximum number of attempts to place the element.
        """

        assert isinstance(element, SceneElement)

        if element in self.elements:
            raise ValueError('Scene Element already in Playground')

        if initial_coordinates:
            element.initial_coordinates = initial_coordinates

        # If element already has a positioning strategy, use it
        element.overlapping_strategy = (
            allow_overlapping,
            max_attempts,
        )

        self._add_element_to_playground(element)
        self._move_to_initial_position(element)

    def add_timer(
        self,
        timer: Timer,
        element: InteractiveElement,
    ):

        assert isinstance(timer, Timer) and isinstance(element,
                                                       InteractiveElement)
        assert element in self.elements

        self._timers[timer] = element

    # Private methods for Agents

    def _add_agent_to_playground(self, agent: Agent):

        self.agents.append(agent)

        for body_part in agent.parts:
            self.space.add(*body_part.pm_elements)

    def _add_communication_devices(self, agent: Agent):

        if agent.communication:
            self.communication_devices.append(agent.communication)
            self.space.add(agent.communication.pm_shape)
            agent.communication.playground = self

    def _add_sensor_devices(self, agent: Agent):

        # Set the invisible element filters
        for sensor in agent.sensors:

            self._sensor_devices.append(sensor)
            self.space.add(sensor.pm_shape)
            sensor.set_playground_size(self.size)

    # Private methods for Elements

    def _add_element_to_playground(self, element: SceneElement):

        if element in self.elements:
            raise ValueError('Scene element already in Playground')

        if element in self._disappeared_elements:
            self._disappeared_elements.remove(element)

        self.space.add(*element.pm_elements)
        self.elements.append(element)

        element.playground = self

    # Private methods for Agents and Elements

    def _move_to_initial_position(self, entity: Union[SceneElement, Agent]):

        allow_overlapping, max_attempts = entity.overlapping_strategy

        if allow_overlapping:
            entity.coordinates = entity.initial_coordinates
            return True

        attempt = 0
        success = False

        while (not success) and (attempt < max_attempts):
            entity.coordinates = entity.initial_coordinates
            success = not ((self._overlaps(entity)
                            or self._out_of_playground(entity)))
            attempt += 1

        if success:
            return True

        raise ValueError('Entity could not be placed without overlapping')

    # Entities

    def _out_of_playground(self, entity: Union[Agent, SceneElement]) -> bool:

        if (not 0 < entity.position[0] < self._width
                or not 0 < entity.position[1] < self._length):
            return True

        return False

    def _remove_element_from_playground(self, element: SceneElement):

        assert element in self.elements

        self.space.remove(*element.pm_elements)
        self.elements.remove(element)

        if not element.temporary:
            self._disappeared_elements.append(element)

        dispensers = [
            elem for elem in self.elements if isinstance(elem, Dispenser)
        ]

        for dispenser in dispensers:
            if element in dispenser.produced_entities:
                dispenser.produced_entities.remove(element)

        for spawner in self.spawners:
            if element in spawner.produced_entities:
                spawner.produced_entities.remove(element)

        for grasper in element.held_by:
            grasper.release_grasp()

        element.playground = False

        return True

    def remove_add_within(
        self,
        elems_remove: Optional[List[SceneElement]],
        elems_add: Optional[List[Tuple[SceneElement, InitCoord]]],
    ):

        if elems_remove:
            for elem in elems_remove:
                self._remove_element_from_playground(elem)

        if elems_add:
            for elem, coordinates in elems_add:
                self._add_element_to_playground(elem)
                if coordinates:
                    elem.coordinates = coordinates
                else:
                    self._move_to_initial_position(elem)

    def _spawners_produce(self):

        for spawner in self.spawners:
            elem_list = spawner.produce(self._timestep)

            for element, position in elem_list:
                allow_overlapping = spawner.allow_overlapping
                if isinstance(element, SceneElement):
                    self.add_element(
                        element,
                        position,
                        allow_overlapping=allow_overlapping,
                    )
                elif isinstance(element, Agent):
                    self.add_agent(
                        element,
                        position,
                        allow_overlapping=allow_overlapping,
                    )
                else:
                    raise ValueError('Spawners can only produce SceneElements or Agents')

    def _update_timers(self):

        for timer, element in self._timers.items():

            timer.step()
            if timer.tic:
                elems_remove, elems_add = element.activate(timer)
                self.remove_add_within(elems_remove, elems_add)

    def _release_grasps(self):

        for agent in self.agents:

            for actuator in agent.actuators:

                # if agent is not holding anymore
                if isinstance(actuator, Grasp):

                    if actuator.is_holding and not actuator.grasped:
                        actuator.is_holding = False

                    # if agent is not holding anymore
                    if not actuator.is_holding:

                        for joint in actuator.grasped:
                            self.space.remove(joint)
                        actuator.grasped = []

        for element_grasped, actuator in self._grasped_elements.copy().items():
            if not actuator.grasped:
                self._grasped_elements.pop(element_grasped)

    # def _check_teleports(self):
    #
    #     for agent, teleport in self._teleported.copy():
    #
    #         overlaps = self._overlaps(agent, teleport)
    #         if not overlaps and not agent.is_teleporting:
    #             self._teleported.remove((agent, teleport))

    # Overlaps

    def _overlaps(
        self,
        entity: Union[Agent, Part, SceneElement],
        entity_2: Optional[Union[Part, SceneElement]] = None,
        entity_filter: Optional[List[Union[Part, SceneElement]]] = None,
    ) -> bool:

        filter_shapes = []
        if entity_filter:
            filter_shapes = [ent.pm_visible_shape for ent in entity_filter]

        if isinstance(entity, Agent):

            if not entity_filter:
                entity_filter = entity.parts  # type: ignore
            else:
                entity_filter += entity.parts

            for part in entity.parts:
                if self._overlaps(part, entity_filter=entity_filter):
                    return True

            return False

        assert entity.pm_visible_shape

        if entity_2 and entity_2.pm_visible_shape:

            collisions = entity.pm_visible_shape.shapes_collide(
                entity_2.pm_visible_shape)

            if collisions:
                return True
            return False

        shape_queries = self.space.shape_query(entity.pm_visible_shape)
        overlapping_shapes = [shape_q.shape for shape_q in shape_queries]
        overlapping_shapes = [
            shape for shape in overlapping_shapes
            if shape and not shape.sensor and shape not in filter_shapes
        ]

        if overlapping_shapes:
            return True

        return False

    def _get_element_from_shape(
        self,
        pm_shape: pymunk.Shape,
    ) -> Optional[SceneElement]:
        return next(
            iter([e for e in self.elements if pm_shape in e.pm_elements]),
            None)

    def _get_device_from_shape(
        self,
        pm_shape: pymunk.Shape,
    ) -> Optional[Device]:

        device = next(
            iter([e for e in self.communication_devices if pm_shape is e.pm_shape]),
            None)
        if device:
            return device

        device = next(
            iter([e for e in self._sensor_devices if pm_shape is e.pm_shape]),
            None)
        if device:
            return device

        return None

    def _get_agent_from_shape(self,
                              pm_shape: pymunk.Shape) -> Union[None, Agent]:
        for agent in self.agents:
            if agent.owns_shape(pm_shape):
                return agent
        return None

    def _get_agent_from_part(self, part: Part) -> Optional[Agent]:
        for agent in self.agents:
            if part in agent.parts:
                return agent
        return None

    def get_entity_from_shape(
            self,
            pm_shape: pymunk.Shape) -> Optional[Union[Part, SceneElement]]:

        element = self._get_element_from_shape(pm_shape)
        if element:
            return element

        for agent in self.agents:

            part = agent.get_part_from_shape(pm_shape)
            if part:
                return part

        for device in self.communication_devices + self._sensor_devices:
            if device.pm_shape is pm_shape:
                return device

        return None

    def get_closest_agent(self, element: SceneElement) -> Agent:
        return min(self.agents,
                   key=lambda a: element.position.get_dist_sqrd(a.position))

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
