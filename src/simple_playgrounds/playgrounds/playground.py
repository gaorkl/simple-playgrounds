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

if TYPE_CHECKING:
    from ..agents.communication import CommunicationDevice
    from ..agents.sensors.sensor import SensorDevice
    from ..agents.communication import CommunicationDevice
    from ..agents.parts.parts import Part
    from ..common.position_utils import InitCoord

import pymunk

from simple_playgrounds.common.definitions import PYMUNK_STEPS


from ..common.definitions import SPACE_DAMPING, CollisionTypes
from ..common.timer import Timer

from ..elements.element import SceneElement
from ..agents.agent import Agent
from ..agents.parts.actuators import Grasp, Activate
from ..elements.field import Field
from ..elements.collection.activable import Dispenser

from ..elements.collection.modifier import ModifierElement
from ..common.devices import Device
from ..elements.element import InteractiveElement

from ..elements.collection.gem import GemElement
from ..elements.collection.teleport import TeleportElement


# pylint: disable=unused-argument
# pylint: disable=line-too-long


class Playground(ABC):
    """ Playground is a Base Class that manages the physical simulation.

    Playground manages the interactions between Agents and Scene Elements.

    Attributes:
        size: size of the scene (width, length).
        elements: list of SceneElements present in the Playground.
        fields: list of fields producing SceneElements in the Playground.
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
        self._space = self._initialize_space()

        # Public attributes for entities in the playground
        self.elements: List[SceneElement] = []
        self.fields: List[Field] = []
        self.agents: List[Agent] = []

        self._communication_devices: List[CommunicationDevice] = []
        self._sensor_devices: List[SensorDevice] = []

        # Private attributes for managing interactions in playground
        self._disappeared_elements: List[SceneElement] = []
        self._grasped_elements: Dict[SceneElement, Grasp] = {}
        self._teleported: List[Tuple[Agent, SceneElement]] = []

        # Timers to handle periodic events
        self._timers: Dict[Timer, InteractiveElement] = {}

        self.done = False
        self.initial_agent_coordinates: Optional[InitCoord] = None

        self._handle_interactions()
        self.sensor_collision_index = 2

        # Timestep index. Starts at 0, and is incremented after each playground update.
        self._step = 0

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

        Update all SceneElements, Fields, Timers and Grasps
        Runs the Physics engine for n steps.

        Args:
            pymunk_steps: Number of steps

        """

        # Update the state of all elements and interactions
        self._update_spawners()
        self._update_grasps()
        self._update_teleports()

        # Update timers
        self._update_timers()

        # Agents communicate before moving
        self._update_communications()

        self._simulator_step(pymunk_steps)

    def _simulator_step(self, pymunk_steps):

        self._entities_pre_step()

        for _ in range(pymunk_steps):
            self._space.step(1. / pymunk_steps)

        self._step += 1

    def _update_communications(self):
        # Update Comms after the simulation step
        for comm in self._communication_devices:
            comm.pre_step()

        for comm in self._communication_devices:
            comm.update_list_comms_in_range(self._communication_devices)

    def _entities_pre_step(self):

        for agent in self.agents:
            agent.pre_step()

        for elem in self.elements:
            elem.pre_step()
            if elem.trajectory:
                self._space.reindex_shapes_for_body(elem.pm_body)

    def reset(self):
        """
        Reset the Playground to its initial state.
        """

        # remove entities which are temporary. Reset the others
        for element in self.elements.copy():
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

        # reset fields
        for field in self.fields:
            field.reset()

        # reset agents
        for agent in self.agents.copy():
            agent.reset()
            self._move_to_initial_position(agent)

        # reset timers
        for timer in self._timers:
            timer.reset()

        # reset communication devices
        for comm in self._communication_devices:
            comm.reset()

        self._teleported = []

        self.done = False

        self._step = 0

    def add_agent(
        self,
        agent: Agent,
        initial_coordinates: Optional[InitCoord] = None,
        allow_overlapping: Optional[bool] = True,
        max_attempts: Optional[int] = 100,
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

    def remove_agent(self, agent: Agent):
        """
        Removes an agent from a playground.

        Args:
            agent: Agent to remove.

        """

        assert agent in self.agents

        agent.reset()
        for part in agent.parts:
            self._space.remove(*part.pm_elements)

        if agent.can_communicate:
            self._communication_devices.remove(agent.communication)
            self._space.remove(agent.communication.pm_shape)

        for sensor in agent.sensors:
            self._sensor_devices.remove(sensor)
            self._space.remove(sensor.pm_shape)

        self.agents.remove(agent)
        assert not agent.in_playground

    def add_field(self, field: Field):

        assert isinstance(field, Field)

        # If already there
        if field in self.fields:
            raise ValueError('Field already in Playground')

        self.fields.append(field)

    def add_element(
        self,
        element: SceneElement,
        initial_coordinates: Optional[InitCoord] = None,
        allow_overlapping: Optional[bool] = True,
        max_attempts: Optional[int] = 100,
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
            self._space.add(*body_part.pm_elements)

    def _add_communication_devices(self, agent: Agent):

        if agent.can_communicate:
            self._communication_devices.append(agent.communication)
            self._space.add(agent.communication.pm_shape)

    def _add_sensor_devices(self, agent: Agent):

        # Set the invisible element filters
        for sensor in agent.sensors:

            self._sensor_devices.append(sensor)
            self._space.add(sensor.pm_shape)

            if sensor.requires_scale:
                sensor.set_scale(self.size)

    # Private methods for Elements

    def _add_element_to_playground(self, element: SceneElement):

        if element in self.elements:
            raise ValueError('Scene element already in Playground')

        if element in self._disappeared_elements:
            self._disappeared_elements.remove(element)

        self._space.add(*element.pm_elements)
        self.elements.append(element)

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

        self._space.remove(*element.pm_elements)
        self.elements.remove(element)

        if not element.temporary:
            self._disappeared_elements.append(element)

        dispensers = [
            elem for elem in self.elements if isinstance(elem, Dispenser)
        ]

        for dispenser in dispensers:
            if element in dispenser.produced_entities:
                dispenser.produced_entities.remove(element)

        for field in self.fields:
            if element in field.produced_entities:
                field.produced_entities.remove(element)

        if element in self._grasped_elements.keys():
            actuator = self._grasped_elements[element]
            self._space.remove(*actuator.grasped)
            actuator.grasped = []

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

    def _update_spawners(self):

        for field in self.fields:

            if field.can_produce():
                element, position = field.produce()
                self.add_element(element, position)

    def _update_timers(self):

        for timer, element in self._timers.items():

            timer.step()
            if timer.tic:
                elems_remove, elems_add = element.activate(timer)
                self.remove_add_within(elems_remove, elems_add)

    def _update_grasps(self):

        for agent in self.agents:

            for actuator in agent.actuators:

                # if agent is not holding anymore
                if isinstance(actuator, Grasp):

                    if actuator.is_holding and not actuator.grasped:
                        actuator.is_holding = False

                    # if agent is not holding anymore
                    if not actuator.is_holding:

                        for joint in actuator.grasped:
                            self._space.remove(joint)
                        actuator.grasped = []

        for element_grasped, actuator in self._grasped_elements.copy().items():
            if not actuator.grasped:
                self._grasped_elements.pop(element_grasped)

    def _update_teleports(self):

        for agent, teleport in self._teleported.copy():

            overlaps = self._overlaps(agent, teleport)
            if not overlaps and not agent.is_teleporting:
                self._teleported.remove((agent, teleport))

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

        else:
            assert entity.pm_visible_shape

        if entity_2 and entity_2.pm_visible_shape:

            collisions = entity.pm_visible_shape.shapes_collide(
                entity_2.pm_visible_shape)

            if collisions:
                return True
            return False

        shape_queries = self._space.shape_query(entity.pm_visible_shape)
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
            iter([e for e in self._communication_devices if pm_shape is e.pm_shape]),
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

        return None

    def _get_closest_agent(self, element: SceneElement) -> Agent:
        return min(self.agents,
                   key=lambda a: element.position.get_dist_sqrd(a.position))

    def _handle_interactions(self):

        # Order is important

        self.add_interaction(CollisionTypes.PART, CollisionTypes.GRASPABLE,
                             self._agent_grasps_element)
        self.add_interaction(CollisionTypes.PART, CollisionTypes.CONTACT,
                             self._agent_touches_element)
        self.add_interaction(CollisionTypes.PART, CollisionTypes.ACTIVABLE,
                             self._agent_activates_element)
        self.add_interaction(CollisionTypes.GEM,
                             CollisionTypes.ACTIVABLE_BY_GEM,
                             self._gem_activates_element)
        self.add_interaction(CollisionTypes.PART, CollisionTypes.TELEPORT,
                             self._agent_teleports)
        self.add_interaction(CollisionTypes.MODIFIER, CollisionTypes.DEVICE,
                             self._modifier_modifies_device)

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

        handler = self._space.add_collision_handler(collision_type_1,
                                                    collision_type_2)
        handler.pre_solve = interaction_function


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
