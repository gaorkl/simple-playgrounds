""" Contains the base class for Playgrounds.

Playground class should be inherited to create environments
where agents can play.
Playground defines the physics and mechanics of the game, and manages
how entities interact with each other.

Examples can be found in :
    - simple_playgrounds/playgrounds/empty.py
    - simple_playgrounds/playgrounds/collection
"""

from typing import Tuple, Union, List, Dict, TYPE_CHECKING
if TYPE_CHECKING:
    from simple_playgrounds.utils.definitions import InitCoord
    from simple_playgrounds.entity import Entity

from abc import ABC
import pymunk

from simple_playgrounds.utils.position_utils import CoordinateSampler
from simple_playgrounds.utils.definitions import SPACE_DAMPING, CollisionTypes

from simple_playgrounds.agents.agent import Agent
from simple_playgrounds.agents.parts import Part
from simple_playgrounds.elements.element import SceneElement,\
    InteractiveElement, ContactElement, ActivableElement, GemElement, TeleportElement
from simple_playgrounds.elements.production_field import Field
from simple_playgrounds.agents.sensors import RayCollisionSensor

from simple_playgrounds.utils.timer import Timer
from simple_playgrounds.elements import Dispenser


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

    def __init__(self,
                 size: Tuple[int, int]
                 ):

        # Generate Scene
        self.size = size
        self._width, self._length = self.size

        # Initialization of the pymunk space, modelling all the physics
        self.space = self._initialize_space()

        # Public attributes for entities in the playground
        self.elements: List[SceneElement] = []
        self.fields: List[Field] = []
        self.agents: List[Agent] = []

        # Private attributes for managing interactions in playground
        self._disappeared_scene_elements: List[SceneElement] = []
        self._grasped_elements: Dict[SceneElement, Part] = {}
        self._teleported: List[Tuple[Agent, SceneElement]] = []

        # Timers to handle periodic events
        self._timers: Dict[Timer, InteractiveElement] = {}

        self.done = False
        self.initial_agent_coordinates = None

        self._handle_interactions()
        self.sensor_collision_index = 2

    @staticmethod
    def _initialize_space() -> pymunk.Space:
        """ Method to initialize Pymunk empty space for 2D physics.

        Returns: Pymunk Space

        """
        space = pymunk.Space()
        space.gravity = pymunk.Vec2d(0., 0.)
        space.damping = SPACE_DAMPING

        return space

    def update(self, steps: int):
        """ Update the Playground

        Update all SceneElements, Fields, Timers and Grasps
        Runs the Physics engine for n steps.

        Args:
            steps: Number of steps

        """

        for agent in self.agents:
            agent.pre_step()

        for _ in range(steps):
            self.space.step(1. / steps)

        for elem in self.elements:
            elem.pre_step()
            if elem.follows_waypoints:
                self.space.reindex_shapes_for_body(elem.pm_body)

        self._fields_produce()
        self._update_timers()
        self._release_grasps()
        self._check_teleports()

    def reset(self):
        """
        Reset the Playground to its initial state.
        """

        # remove entities which are temporary. Reset the others
        for element in self.elements:
            if element.is_temporary_entity:
                self._remove_element_from_playground(element)
            else:
                element.reset()
                self._move_to_initial_position(element)

        # reset and replace entities that are not temporary
        for element in self._disappeared_scene_elements:
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

        self.done = False

    def add_agent(self,
                  agent: Agent,
                  initial_coordinates: InitCoord = None,
                  allow_overlapping: bool = True,
                  max_attempts: int = 100,
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
        agent.overlapping_strategy = (allow_overlapping,
                                      max_attempts,
                                      )

        # Set initial position. Either set or from playground.
        if initial_coordinates:
            agent.initial_coordinates = initial_coordinates
        elif self.initial_agent_coordinates:
            agent.initial_coordinates = self.initial_agent_coordinates
        else:
            raise ValueError("""Agent initial position should be defined in the playground or passed as an argument)
                             to the class agent""")

        self._add_agent_to_playground(agent)
        self._set_sensor_filters(agent)
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
            self.space.remove(*part.pm_elements)

        self.agents.remove(agent)
        agent.in_a_playground = False

    def add_field(self, field: Field):

        assert isinstance(field, Field)

        # If already there
        if field in self.fields:
            raise ValueError('Field already in Playground')

        self.fields.append(field)

    def add_element(self,
                    element: SceneElement,
                    initial_coordinates: InitCoord = None,
                    allow_overlapping: bool = True,
                    max_attempts: int = 100,
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

        # If agent already has a positioning strategy, use it
        element.overlapping_strategy = (allow_overlapping,
                                        max_attempts,
                                        )
        self._add_element_to_playground(element)
        self._move_to_initial_position(element)

    def add_timer(self,
                  timer: Timer,
                  element: InteractiveElement,
                  ):

        assert isinstance(timer, Timer) and isinstance(element, InteractiveElement)
        assert element in self.elements

        self._timers[timer] = element

    # Private methods for Agents

    def _add_agent_to_playground(self, agent: Agent):

        self.agents.append(agent)
        agent.in_a_playground = True

        for body_part in agent.parts:
            self.space.add(*body_part.pm_elements)

    def _set_sensor_filters(self, agent: Agent):

        # Set the invisible element filters
        for sensor in agent.sensors:
            if isinstance(sensor, RayCollisionSensor) and sensor.invisible_elements:

                sensor.apply_shape_filter(self.sensor_collision_index)
                self.sensor_collision_index += 1

                if self.sensor_collision_index == 32:
                    raise ValueError('Too many sensors using invisible shapes. Pymunk limits them to 32.')

    # Private methods for Elements

    def _add_element_to_playground(self, element: SceneElement):

        if element in self.elements:
            raise ValueError('Scene element already in Playground')

        if element in self._disappeared_scene_elements:
            self._disappeared_scene_elements.remove(element)

        self.space.add(*element.pm_elements)
        self.elements.append(element)

    # Private methods for Agents and Elements

    def _move_to_initial_position(self, entity: Union[SceneElement, Agent]):

        allow_overlapping, max_attempts = entity.overlapping_strategy

        if allow_overlapping:
            entity.coordinates = entity.initial_coordinates

            return True

        attempt = 0
        success = False

        while (not success) or (attempt > max_attempts):
            entity.coordinates = entity.initial_coordinates
            success = not (self._overlaps(entity) or self._out_of_playground(entity))
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

        if not element.is_temporary_entity:
            self._disappeared_scene_elements.append(element)

        for elem in self.elements:
            if isinstance(elem, Dispenser) and element in elem.produced_entities:
                elem.produced_entities.remove(element)

        for field in self.fields:
            if element in field.produced_entities:
                field.produced_entities.remove(element)

        if element in self._grasped_elements.keys():
            body_part = self._grasped_elements[element]
            self.space.remove(*body_part.grasped)
            body_part.grasped = []

        return True

    def _fields_produce(self):

        for field in self.fields:

            if field.can_produce():
                element, position = field.produce()
                self.add_element(element, position)

    def _update_timers(self):

        for timer, element in self._timers.items():
            timer.step()
            if timer.timer_done:
                elems_remove, elems_add = element.activate()

                for elem in elems_remove:
                    self._remove_element_from_playground(elem)

                for elem, coordinates in elems_add:
                    self._add_element_to_playground(elem)
                    if coordinates:
                        elem.coordinates = coordinates
                    else:
                        self._move_to_initial_position(elem)

    def _release_grasps(self):

        for agent in self.agents:

            for part in agent.parts:
                if not part.is_holding and part.can_grasp:

                    for joint in part.grasped:
                        self.space.remove(joint)
                    part.grasped = []

        for element_grasped, part in self._grasped_elements.copy().items():
            if not part.grasped:
                self._grasped_elements.pop(element_grasped)

    def _check_teleports(self):

        for agent, teleport in self._teleported.copy():

            overlaps = self._overlaps(agent, teleport)

            if not overlaps and not agent.is_teleporting:
                self._teleported.remove((agent, teleport))

    # Overlaps

    def _overlaps(self,
                  entity_1: Union[Agent, Part, SceneElement],
                  entity_2: Union[None, Union[Agent, Part, SceneElement]] = None,
                  entity_filter: Tuple[Entity] = (),
                  ) -> bool:

        filter_shapes = [ent.pm_visible_shape for ent in entity_filter]

        if isinstance(entity_1, Agent):

            for part in entity_1.parts:
                if self._overlaps(part, entity_2, entity_filter=entity_1.parts):
                    return True

        if isinstance(entity_2, Agent):

            for part in entity_2.parts:
                if self._overlaps(entity_1, part, entity_filter=entity_2.parts):
                    return True

        if entity_2 is None:
            possible_overlapping_shapes = [shape for shape in self.space.shapes.copy()
                                           if not shape.sensor
                                           and shape not in filter_shapes]

        else:
            possible_overlapping_shapes = [entity_2.pm_visible_shape]

        for shape in possible_overlapping_shapes:
            if entity_1.pm_visible_shape.shapes_collide(shape):
                return True

        return False

    def _get_element_from_shape(self, pm_shape: pymunk.Shape):
        return next(iter([e for e in self.elements if pm_shape in e.pm_elements]), None)

    def _get_agent_from_shape(self, pm_shape: pymunk.Shape) -> Union[None, Agent]:
        for agent in self.agents:
            if agent.owns_shape(pm_shape):
                return agent
        return None

    def get_entity_from_shape(self, pm_shape: pymunk.Shape) -> Union[None, Part, SceneElement]:

        element = self._get_element_from_shape(pm_shape)
        if element:
            return element

        for agent in self.agents:

            part = agent.get_part_from_shape(pm_shape)
            if part is not None:
                return part

        return None

    def _get_closest_agent(self, element: SceneElement) -> Agent:
        return min(self.agents, key=lambda a: element.position.get_dist_sqrd(a))

    def _agent_touches_element(self, arbiter, space, data):

        agent: Agent = self._get_agent_from_shape(arbiter.shapes[0])
        touched_element = self._get_element_from_shape(arbiter.shapes[1])

        if not touched_element:
            return True

        assert isinstance(touched_element, ContactElement)

        agent.reward += touched_element.reward

        elems_remove, elems_add = touched_element.activate()

        for elem in elems_remove:
            self._remove_element_from_playground(elem)

        for elem, coordinates in elems_add:
            self._add_element_to_playground(elem)
            if coordinates:
                elem.coordinates = coordinates
            else:
                self._move_to_initial_position(elem)

        if touched_element.terminate_upon_activation:
            self.done = True

        return True

    def _agent_activates_element(self, arbiter, space, data):

        agent: Agent = self._get_agent_from_shape(arbiter.shapes[0])
        part: Part = agent.get_part_from_shape(arbiter.shapes[0])
        activable_element = self._get_element_from_shape(arbiter.shapes[1])

        assert isinstance(activable_element, ActivableElement)

        if part.is_activating:

            agent.reward += activable_element.reward

            elems_remove, elems_add = activable_element.activate()

            for elem in elems_remove:
                self._remove_element_from_playground(elem)

            for elem, coordinates in elems_add:
                self._add_element_to_playground(elem)
                if coordinates:
                    elem.coordinates = coordinates
                else:
                    self._move_to_initial_position(elem)

            if activable_element.terminate_upon_activation:
                self.done = True

            part.is_activating = False

        return True

    def _agent_grasps_element(self, arbiter, space, data):

        agent: Agent = self._get_agent_from_shape(arbiter.shapes[0])
        part: Part = agent.get_part_from_shape(arbiter.shapes[0])
        grasped_element = self._get_element_from_shape(arbiter.shapes[1])

        assert grasped_element.graspable

        if part.is_grasping and not part.is_holding:
            part.is_holding = True

            j_1 = pymunk.PinJoint(part.pm_body, grasped_element.pm_body, (0, 5), (0, 0))
            j_2 = pymunk.PinJoint(part.pm_body, grasped_element.pm_body, (0, -5), (0, 0))
            motor = pymunk.SimpleMotor(part.pm_body, grasped_element.pm_body, 0)

            self.space.add(j_1, j_2, motor)
            part.grasped = [j_1, j_2, motor]

            self._grasped_elements[grasped_element] = part

        return True

    def _gem_activates_element(self, arbiter, space, data):

        gem = self._get_element_from_shape(arbiter.shapes[0])
        activable_element = self._get_element_from_shape(arbiter.shapes[1])

        assert isinstance(gem, GemElement)
        assert isinstance(activable_element, InteractiveElement)

        agent = self._get_closest_agent(gem)

        agent.reward += activable_element.reward

        elems_remove, elems_add = activable_element.activate()

        for elem in elems_remove:
            self._remove_element_from_playground(elem)

        for elem, coordinates in elems_add:
            self._add_element_to_playground(elem)
            if coordinates:
                elem.coordinates = coordinates
            else:
                self._move_to_initial_position(elem)

        if activable_element.terminate_upon_activation:
            self.done = True

        return True

    def _agent_teleports(self, arbiter, space, data):

        agent = self._get_agent_from_shape(arbiter.shapes[0])
        teleport = self._get_element_from_shape(arbiter.shapes[1])

        assert isinstance(teleport, TeleportElement)

        if teleport is None or teleport.target is None or (agent, teleport) in self._teleported:
            return True

        if agent.is_teleporting:
            return True

        if teleport.target.traversable:

            agent.position = teleport.target.position

        else:
            area_shape = teleport.target.physical_shape
            if area_shape == 'rectangle':
                width = teleport.target.width + agent.base_platform.radius * 2 + 1
                length = teleport.target.length + agent.base_platform.radius * 2 + 1
                angle = teleport.target.angle
                sampler = CoordinateSampler(
                    center=teleport.target.position,
                    area_shape=area_shape,
                    angle=angle,
                    width_length=[width + 2, length + 2],
                    excl_width_length=[width, length],
                )
            else:
                radius = teleport.target.radius + agent.base_platform.radius + 1
                sampler = CoordinateSampler(
                    center=teleport.target.position,
                    area_shape='circle',
                    radius=radius,
                    excl_radius=radius,
                )

            agent.coordinates = sampler.sample()

        if (agent, teleport.target) not in self._teleported:
            self._teleported.append((agent, teleport.target))

        agent.is_teleporting = True

        return True

    def _handle_interactions(self):

        # Order is important

        self.add_interaction(CollisionTypes.AGENT, CollisionTypes.GRASPABLE, self._agent_grasps_element)
        self.add_interaction(CollisionTypes.AGENT, CollisionTypes.CONTACT, self._agent_touches_element)
        self.add_interaction(CollisionTypes.AGENT, CollisionTypes.INTERACTIVE, self._agent_activates_element)
        self.add_interaction(CollisionTypes.GEM, CollisionTypes.INTERACTIVE, self._gem_activates_element)
        self.add_interaction(CollisionTypes.AGENT, CollisionTypes.TELEPORT, self._agent_teleports)

    def add_interaction(self, collision_type_1, collision_type_2, interaction_function):
        """

        Args:
            collision_type_1: collision type of the first entity
            collision_type_2: collision type of the second entity
            interaction_function: function that handles the interaction

        Returns: None

        """

        handler = self.space.add_collision_handler(collision_type_1, collision_type_2)
        handler.pre_solve = interaction_function


class PlaygroundRegister:
    """
    Class to register Playgrounds.
    """

    playgrounds: Dict[str, Dict[str, Playground]] = {}

    @classmethod
    def register(cls,
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
