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
from typing import Union, List, Dict, Optional, Type, TYPE_CHECKING

if TYPE_CHECKING:
    from simple_playgrounds.agents.communication import CommunicationDevice
    from simple_playgrounds.agents.sensors.sensor import SensorDevice
    from simple_playgrounds.agents.communication import CommunicationDevice
    from simple_playgrounds.agents.parts.parts import Part
    from simple_playgrounds.common.position_utils import InitCoord

import pymunk

from simple_playgrounds.common.definitions import PYMUNK_STEPS

from simple_playgrounds.playgrounds.interactions import (gem_activates_element,
                                                         agent_activates_element,
                                                         agent_touches_element,
                                                         agent_grasps_element,
                                                         agent_teleports,
                                                         modifier_modifies_device
                                                         )

from simple_playgrounds.common.definitions import SPACE_DAMPING, CollisionTypes, MAX_ATTEMPTS_OVERLAPPING
from simple_playgrounds.base.timer import Timer

from simple_playgrounds.elements.element import SceneElement
from simple_playgrounds.agents.agent import Agent
from simple_playgrounds.elements.spawner import Spawner
from simple_playgrounds.base.device import Device


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

    def __init__(
            self,
    ):

        # Initialization of the pymunk space, modelling all the physics
        self.space = self._initialize_space()

        # Public attributes for entities in the playground
        self.elements: List[SceneElement] = []
        self.spawners: List[Spawner] = []
        self.agents: List[Agent] = []

        # Store devices for easy updates
        self.communication_devices: List[CommunicationDevice] = []
        self._sensor_devices: List[SensorDevice] = []

        # Store elements that are removed but should be respawned after reset.
        self._disappeared_elements: List[SceneElement] = []

        # Timers to handle periodic events
        self._timers: List[Timer] = []

        self.done = False
        self.initial_agent_coordinates: Optional[InitCoord] = None

        self._handle_interactions()

        # Timestep index. Starts at 0, and is incremented after each playground update.
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

        # Update the state of all elements and interactions
        self._update_spawners()

        # Update timers
        self._update_timers()

        # Agents communicate before physical steps
        self._update_communications()

        # Update all entities and interactions before physical steps
        self._update_entities()

        # Move one timestep by pymunk_steps increments
        self._physics_simulator_step(pymunk_steps)

    def update_sensors(self):

        for sensor in self._sensor_devices:
            sensor.update()

    @property
    def timestep(self):
        return self._timestep

    def add(self, entity, **kwargs):
        """ Method to add a SceneElement to the Playground.

        Args:
            entity: Scene Element to add to the Playground

        Keyword Args:
            initial_coordinates: initial position and angle of the SceneElement.
                Can be list [x,y,theta], AreaPositionSampler or Trajectory.
            allow_overlapping: If True, allows new elements to overlap with other elements when added to the Playground.
            max_attempts: If overlapping is not allowed, maximum number of attempts to place the element.
        """

        if isinstance(entity, Spawner):
            if entity in self.spawners:
                raise ValueError('Spawner already in Playground')
            entity.add_to_playground(self)
            self.spawners.append(entity)

        if isinstance(entity, Agent):
            self._add_agent(entity, **kwargs)

        if isinstance(entity, SceneElement):
            self._add_element(entity)

    def remove(self, entity: Union[Agent, SceneElement], definitive=False):

        if isinstance(entity, Agent):
            if entity not in self.agents:
                raise ValueError('Agent {} already removed or not in Playground'.format(entity.name))
            self.agents.remove(entity)

        elif isinstance(entity, SceneElement):

            if entity.held_by:
                entity.held_by.release_grasp()

            if entity not in self.elements:
                raise ValueError('Element {} already removed or not in Playground'.format(entity.name))
            self.elements.remove(entity)

        if entity.produced_by:
            entity.produced_by.produced.remove(entity)

        entity.remove_from_playground()

        if definitive or entity.temporary:
            return

        self._disappeared_elements.append(entity)

    def reset(self):
        """
        Reset the Playground to its initial state.
        """

        # remove entities which are temporary. Reset the others
        for element in self.elements.copy():
            if element.held_by:
                element.held_by.release_grasp()

            if element.temporary:
                element.remove_from_playground()
            else:
                element.reset()
                self._move_to_initial_position(element)

        # reset and replace entities that are not temporary
        for element in self._disappeared_elements.copy():
            element.reset()
            self.add(element)

        # reset fields
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
        for sens in self._sensor_devices:
            sens.reset()

        self.done = False
        self._timestep = 0

    def _add_agent(
            self,
            agent: Agent,
            **kwargs,
    ):

        # If already there
        if agent in self.agents:
            raise ValueError('Agent already in Playground')

        self._set_initial_position(agent, **kwargs)

        agent.add_to_playground(self)
        self._move_to_initial_position(agent)
        self.agents.append(agent)

    def _add_element(
            self,
            element,
            **kwargs,
    ):

        if element in self.elements:
            raise ValueError('Scene Element already in Playground')

        self._set_initial_position(element, **kwargs)

        element.add_to_playground(self)
        self._move_to_initial_position(element)
        self.elements.append(element)

    def _set_initial_position(self,
                              entity: Union[Agent, SceneElement],
                              initial_coordinates: Optional[InitCoord] = None,
                              allow_overlapping: Optional[bool] = True,
                              max_attempts: Optional[int] = MAX_ATTEMPTS_OVERLAPPING,
                              ):

        entity.overlapping_strategy = allow_overlapping, max_attempts

        # Set initial position. Either set or from playground.
        if initial_coordinates:
            entity.initial_coordinates = initial_coordinates
        elif isinstance(entity, Agent) and self.initial_agent_coordinates:
            entity.initial_coordinates = self.initial_agent_coordinates
        else:
            raise ValueError(
                """Entity {} initial position should be defined in the playground or passed as an argument
                             to the class agent""".format(entity.name))

    def _add_timer(
            self,
            timer: Timer,
    ):

        assert timer.timed_entity.in_playground is self
        self._timers.append(timer)

    def _physics_simulator_step(self, pymunk_steps):

        for _ in range(pymunk_steps):
            self.space.step(1. / pymunk_steps)

        self._timestep += 1

    def _update_communications(self):
        # Update Comms after the simulation step
        for comm in self.communication_devices:
            comm.pre_step()

    def _update_entities(self):

        for agent in self.agents:
            agent.pre_step()

        for elem in self.elements:
            elem.pre_step()
            if elem.trajectory:
                self.space.reindex_shapes_for_body(elem.pm_body)

    # Private methods for Elements

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

    def _update_spawners(self):

        for spawner in self.spawners:
            spawner.produce(self._timestep)

    def _update_timers(self):

        for timer in self._timers:
            timer.update()

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
                entity_filter = entity._parts  # type: ignore
            else:
                entity_filter += entity._parts

            for part in entity._parts:
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
            if part in agent._parts:
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
