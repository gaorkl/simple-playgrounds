""" Contains the base class for Playgrounds.

Playground class should be inherited to create environments
where agents can play.
Playground defines the physics and mechanics of the game, and manages
how entities interact with each other.

Examples can be found in :
    - simple_playgrounds/playgrounds/empty.py
    - simple_playgrounds/playgrounds/collection
"""

from abc import ABC
import pymunk

from simple_playgrounds.utils.position_utils import CoordinateSampler
from simple_playgrounds.utils.definitions import SPACE_DAMPING, CollisionTypes, SceneElementTypes, SensorTypes
from simple_playgrounds.entity import Entity

# pylint: disable=unused-argument
# pylint: disable=line-too-long


class Playground(ABC):
    """ Playground is a Base Class that manages the physical simulation.

    Playground manages the interactions between Agents and Scene Elements.

    Attributes:
        size: size of the scene (width, length).
        scene_elements: list of SceneElements present in the Playground.
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

    def __init__(self, size):

        # Generate Scene
        self.size = size
        self._width, self._length = self.size

        # Initialization of the pymunk space, modelling all the physics
        self.space = self._initialize_space()

        # Public attributes for entities in the playground
        self.scene_elements = []
        self.fields = []
        self.agents = []

        # Private attributes for managing interactions in playground
        self._disappeared_scene_elements = []
        self._grasped_scene_elements = {}
        self._teleported = []

        self.done = False
        self.initial_agent_coordinates = None

        self._handle_interactions()
        self.sensor_collision_index = 2

        self.entity_types_map = {}

    @staticmethod
    def _initialize_space():
        """ Method to initialize Pymunk empty space for 2D physics.

        Returns: Pymunk Space

        """

        space = pymunk.Space()
        space.gravity = pymunk.Vec2d(0., 0.)
        space.damping = SPACE_DAMPING

        return space

    def update(self, steps):
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

        for elem in self.scene_elements:
            elem.pre_step()
            if elem.follows_waypoints:
                self.space.reindex_shapes_for_body(elem.pm_body)

        self._fields_produce()
        self._check_timers()
        self._release_grasps()
        self._check_teleports()

    def reset(self):
        """
        Reset the Playground to its initial state.
        """

        # remove entities and filter out entities which are temporary
        for entity in self.scene_elements.copy():
            self.remove_scene_element(entity)

        # reset and replace entities that are not temporary
        for entity in self._disappeared_scene_elements.copy():
            entity.reset()
            self.add_scene_element(entity)

        # reset fields
        for entity in self.fields:
            entity.reset()

        # reset agents
        for agent in self.agents.copy():
            agent.reset()
            self.move_agent_to_initial_position(agent)

        self.done = False

    def move_agent_to_initial_position(self, agent):
        allow_overlapping, max_attempts, error_if_fails = agent.overlapping_strategy

        if allow_overlapping:
            agent.coordinates = agent.initial_coordinates

        else:
            attempt = 0
            success = False

            while (not success) or (attempt > max_attempts):

                agent.coordinates = agent.initial_coordinates

                agent_collides = self._agent_colliding(agent)

                agent_out = False
                if (not 0 < agent.position[0] < self._width
                        or not 0 < agent.position[1] < self._length):
                    agent_out = True

                success = True
                if agent_collides or agent_out:
                    success = False

                attempt += 1

            if not success:

                msg = 'Agent could not be placed without overlapping'

                if error_if_fails:
                    raise ValueError(msg)

                print(msg)

    def add_agent(self, agent,
                  initial_coordinates=None,
                  keep_coordinates=False,
                  allow_overlapping=True,
                  max_attempts=100,
                  error_if_fails=True):
        """ Method to add an Agent to the Playground.

        Args:
            agent: Agent to add to the Playground
            initial_coordinates: tuple or CoordinateSampler
            keep_coordinates: if True, will not reinitialize position.
            allow_overlapping: If True, allows new agent to overlap with other elements when added to the Playground.
            max_attempts: If overlapping is not allowed, maximum number of attempts to place the agent.
            error_if_fails: If True, an error will be raised if agent can't be placed in the Playground.

        Notes:
            keep_position is useful in the case where agent must disappear and reappear in the same position.
            In this case, the position should not be re-initialized.

        """

        # If already there
        if agent in self.agents:
            raise ValueError('Agent already in Playground')

        # If agent already has a positioning strategy, use it
        if agent.overlapping_strategy is None:
            agent.overlapping_strategy = (allow_overlapping,
                                          max_attempts,
                                          error_if_fails,
                                          )

        # Set initial position
        if initial_coordinates is not None:
            agent.initial_coordinates = initial_coordinates

        # If no initial coordinates, ask playground:
        elif self.initial_agent_coordinates is not None:
            agent.initial_coordinates = self.initial_agent_coordinates

        else:
            raise ValueError("""Agent initial position should be defined in the playground or passed as an argument)
                             to the class agent""")

        self._add_agent(agent, keep_coordinates)
        self._set_sensor_filters(agent)
        self.move_agent_to_initial_position(agent)

    def _set_sensor_filters(self, agent):

        # Set the invisible element filters
        for sensor in agent.sensors:
            if sensor.sensor_modality in [SensorTypes.ROBOTIC, SensorTypes.SEMANTIC]\
                    and sensor.invisible_elements is not None:

                sensor.apply_shape_filter(self.sensor_collision_index)
                self.sensor_collision_index += 1
                if self.sensor_collision_index == 32:
                    raise ValueError('Too many sensors using invisible shapes. Pymunk limits them to 32.')

    def _add_agent(self, agent, keep_position):
        """ Add an agent to the playground.

        Args:
            agent: Agent.

        """
        self.agents.append(agent)
        agent.in_a_playground = True

        if not keep_position:
            agent.coordinates = agent.initial_coordinates

        for body_part in agent.parts:
            self.space.add(*body_part.pm_elements)

    def _agent_colliding(self, agent):

        all_agents_collision_shapes = [part.pm_visible_shape for part in agent.parts]

        all_colliding_shapes = [shape for shape in self.space.shapes
                                if shape not in all_agents_collision_shapes]

        collides = False

        for part in agent.parts:

            collisions = self.space.point_query(part.position, part.radius + 10, pymunk.ShapeFilter())
            collisions = [col for col in collisions if col.shape not in all_agents_collision_shapes]
            collides = collides or len(collisions) != 0

        return collides

    def add_scene_element(self, scene_element,
                          initial_coordinates=None,
                          allow_overlapping=True,
                          max_attempts=100,
                          error_if_fails=True,
                          keep_position=False):
        """ Method to add a SceneElement to the Playground.

        Args:
            scene_element: Scene Element to add to the Playground
            initial_coordinates: initial position and angle of the SceneElement.
                Can be list [x,y,theta], AreaPositionSampler or Trajectory.
            allow_overlapping: If True, allows new elements to overlap with other elements when added to the Playground.
            max_attempts: If overlapping is not allowed, maximum number of attempts to place the element.
            error_if_fails: If True, an error will be raised if an element can't be placed in the Playground.
            keep_position: if True, will not reinitialize position

        Notes:
            keep_position is useful in the case where scene elements must disappear and reappear in the same position.
            In this case, the position should not be re-initialized.

        """

        if scene_element.entity_type is SceneElementTypes.FIELD:

            # If already there
            if scene_element in self.fields:
                raise ValueError('Field already in Playground')

            self.fields.append(scene_element)

        else:
            if scene_element in self.scene_elements:
                raise ValueError('Scene Element already in Playground')

            if initial_coordinates is not None:
                scene_element.initial_coordinates = initial_coordinates

            # If agent already has a positioning strategy, use it
            if scene_element.overlapping_strategy is None:
                scene_element.overlapping_strategy = (allow_overlapping,
                                                      max_attempts,
                                                      error_if_fails,
                                                      )

            else:
                allow_overlapping, max_attempts, error_if_fails = scene_element.overlapping_strategy

            if scene_element.background or allow_overlapping:
                self._add_scene_element(scene_element, keep_position)

            else:

                attempt = 0
                success = False

                while (not success) or (attempt > max_attempts):

                    self._add_scene_element(scene_element, keep_position)
                    if not self._entity_colliding(scene_element):
                        success = True
                    else:
                        self.remove_scene_element(scene_element)
                    attempt += 1

                if not success:

                    msg = 'Scene Element could not be placed without overlapping'

                    if error_if_fails:
                        raise ValueError(msg)

                    print(msg)

    def _add_scene_element(self, new_scene_element, keep_position):

        if new_scene_element in self.scene_elements:
            raise ValueError('Scene element already in Playground')

        if not keep_position:
            new_scene_element.position, new_scene_element.angle = new_scene_element.initial_coordinates

        self.space.add(*new_scene_element.pm_elements)
        self.scene_elements.append(new_scene_element)
        if new_scene_element in self._disappeared_scene_elements:
            self._disappeared_scene_elements.remove(new_scene_element)

    def create_entity_types_map(self,
                                additional_types=[]):
        entity_types = [type(e) for e in self.scene_elements]
        entity_types.extend(additional_types)

        self.entity_types_map = {}
        for et in entity_types:
            if et not in self.entity_types_map:
                self.entity_types_map[et] = len(self.entity_types_map)

    def _entity_colliding(self, entity):

        collides = False

        all_colliding_shapes = [shape for shape in self.space.shapes.copy()
                                if not shape.sensor
                                and shape not in entity.pm_elements]

        if entity.pm_visible_shape is not None:
            collisions = [entity.pm_visible_shape.shapes_collide(shape) for shape in all_colliding_shapes]
            collides = any([len(collision.points) != 0 for collision in collisions])

        return collides

    def _remove_agents(self):

        for agent in self.agents:
            self.remove_agent(agent)

    def remove_agent(self, agent):
        """
        Removes an agent from a playground.

        Args:
            agent: Agent to remove.

        """

        if agent not in self.agents:
            return False

        for part in agent.parts:
            self.space.remove(*part.pm_elements)
            part.velocity = [0, 0]
            part.grasped = []

        if agent.initial_coordinates is self.initial_agent_coordinates:
            agent.initial_coordinates = None

        self.agents.remove(agent)

        agent.in_a_playground = False

        return True

    def remove_scene_element(self, scene_element):
        """
        Removes scene element from the playground.

        Args:
            scene_element: Scene Element to remove.

        """

        if scene_element not in self.scene_elements:
            return False

        self.space.remove(*scene_element.pm_elements)
        self.scene_elements.remove(scene_element)

        if not scene_element.is_temporary_entity:
            self._disappeared_scene_elements.append(scene_element)

        for elem in self.scene_elements:
            if elem.entity_type == SceneElementTypes.DISPENSER and scene_element in elem.produced_entities:
                elem.produced_entities.remove(scene_element)

        for field in self.fields:
            if scene_element in field.produced_entities:
                field.produced_entities.remove(scene_element)

        if scene_element in self._grasped_scene_elements.keys():
            body_part = self._grasped_scene_elements[scene_element]
            self.space.remove(*body_part.grasped)
            body_part.grasped = []

        return True

    def _dynamic_add_remove_elements(self, list_remove, elem_add):

        if list_remove is None:
            pass

        elif isinstance(list_remove, Entity):
            self.remove_scene_element(list_remove)

        elif isinstance(list_remove, (list, tuple)):
            for elem in list_remove:

                if isinstance(elem, Entity):
                    self.remove_scene_element(elem)

                else:
                    raise ValueError('not an entity to remove')

        else:
            raise ValueError('not an entity to remove')

        if elem_add is None:
            pass

        elif isinstance(elem_add, Entity):
            self.add_scene_element(elem_add, keep_position=True)

        elif isinstance(elem_add, tuple):
            elem, pos = elem_add
            self.add_scene_element(elem, pos)

    def _fields_produce(self):

        for field in self.fields:

            if field.can_produce():
                new_entity, position = field.produce()
                self.add_scene_element(new_entity, position)

    def _check_timers(self):

        for entity in self.scene_elements:

            if entity.timed and entity.timer == 0:

                list_remove, elem_add = entity.activate(self)
                self._dynamic_add_remove_elements(list_remove, elem_add)

    def _release_grasps(self):

        for agent in self.agents:

            for part in agent.parts:
                if not part.is_holding and part.can_grasp:

                    for joint in part.grasped:
                        self.space.remove(joint)
                    part.grasped = []

        for element_grasped, part in self._grasped_scene_elements.copy().items():
            if not part.grasped:
                self._grasped_scene_elements.pop(element_grasped)

    def _check_teleports(self):

        for agent, teleport in self._teleported:

            overlaps = self._agent_overlaps_with_element(agent, teleport)

            if not overlaps and not agent.is_teleporting:
                self._teleported.remove((agent, teleport))

    @staticmethod
    def _agent_overlaps_with_element(agent, element):

        overlaps = False

        for part in agent.parts:

            if element.pm_visible_shape is not None:
                overlaps = overlaps or part.pm_visible_shape.shapes_collide(element.pm_visible_shape).points

            if element.pm_interaction_shape is not None:
                overlaps = overlaps or part.pm_visible_shape.shapes_collide(element.pm_interaction_shape).points

        return overlaps

    def _get_scene_element_from_shape(self, pm_shape):
        """
        Returns: Returns the Scene Element associated with the pymunk shape.

        """
        entity = next(iter([e for e in self.scene_elements if pm_shape in e.pm_elements]), None)
        return entity

    def _get_agent_from_shape(self, pm_shape):
        """
        Returns: Returns the Agent associated with the pymunk shape.

        """
        for agent in self.agents:
            if agent.owns_shape(pm_shape):
                return agent

        return None

    def get_entity_from_shape(self, pm_shape):
        """
        Returns the element associated with the pymunk shape

        Args:
            pm_shape: Pymunk shape

        Returns:
            Single entity or None

        """

        scene_element = self._get_scene_element_from_shape(pm_shape)
        if scene_element is not None:
            return scene_element

        for agent in self.agents:

            part = agent.get_bodypart_from_shape(pm_shape)
            if part is not None:
                return part

        return None

    def _get_closest_agent(self, ent):

        dist_list = [(a.position[0] - ent.position[0])**2 + (a.position[1] - ent.position[1])**2 for a in self.agents]
        index_min_dist = dist_list.index(min(dist_list))
        closest_agent = self.agents[index_min_dist]

        return closest_agent

    def _agent_touches_entity(self, arbiter, space, data):

        agent = self._get_agent_from_shape(arbiter.shapes[0])
        touched_entity = self._get_scene_element_from_shape(arbiter.shapes[1])

        if touched_entity is None:
            return True

        agent.reward += touched_entity.reward

        list_remove, list_add = touched_entity.activate()

        for entity_removed in list_remove:
            self.remove_scene_element(entity_removed)

        for entity_added in list_add:
            self.add_scene_element(entity_added)

        if touched_entity.terminate_upon_contact:
            self.done = True

        return True

    def _agent_interacts(self, arbiter, space, data):

        agent = self._get_agent_from_shape(arbiter.shapes[0])
        body_part = agent.get_bodypart_from_shape(arbiter.shapes[0])
        interacting_entity = self._get_scene_element_from_shape(arbiter.shapes[1])

        if interacting_entity is None:
            return True

        if body_part.is_activating:

            agent.reward += interacting_entity.reward

            list_remove, elem_add = interacting_entity.activate(body_part)

            self._dynamic_add_remove_elements(list_remove, elem_add)

            if interacting_entity.terminate_upon_contact:
                self.done = True

            body_part.is_activating = False

        return True

    def _agent_grasps(self, arbiter, space, data):

        agent = self._get_agent_from_shape(arbiter.shapes[0])
        body_part = agent.get_bodypart_from_shape(arbiter.shapes[0])
        interacting_entity = self._get_scene_element_from_shape(arbiter.shapes[1])

        if interacting_entity is None:
            return True

        if body_part.is_grasping and not body_part.is_holding:

            body_part.is_holding = True

            j_1 = pymunk.PinJoint(body_part.pm_body, interacting_entity.pm_body, (0, 5), (0, 0))
            j_2 = pymunk.PinJoint(body_part.pm_body, interacting_entity.pm_body, (0, -5), (0, 0))
            motor = pymunk.SimpleMotor(body_part.pm_body, interacting_entity.pm_body, 0)

            self.space.add(j_1, j_2, motor)
            body_part.grasped = [j_1, j_2, motor]

            self._grasped_scene_elements[interacting_entity] = body_part

        return True

    def _agent_enters_zone(self, arbiter, space, data):

        agent = self._get_agent_from_shape(arbiter.shapes[0])
        zone_reached = self._get_scene_element_from_shape(arbiter.shapes[1])

        if zone_reached is None:
            return True

        agent.reward += zone_reached.reward

        if zone_reached.terminate_upon_contact:
            self.done = True

        return True

    def _gem_interacts(self, arbiter, space, data):

        gem = self._get_scene_element_from_shape(arbiter.shapes[0])
        interacting_entity = self._get_scene_element_from_shape(arbiter.shapes[1])

        if interacting_entity is None or gem is None:
            return True

        agent = self._get_closest_agent(gem)
        agent.reward += interacting_entity.reward

        list_remove, list_add = interacting_entity.activate(gem)

        self._dynamic_add_remove_elements(list_remove, list_add)

        if interacting_entity.terminate_upon_contact:
            self.done = True

        return True

    def _agent_eats(self, arbiter, space, data):

        agent = self._get_agent_from_shape(arbiter.shapes[0])
        body_part = agent.get_bodypart_from_shape(arbiter.shapes[0])
        edible_entity = self._get_scene_element_from_shape(arbiter.shapes[1])

        if edible_entity is None:
            return True

        if body_part.is_eating:

            agent.reward += edible_entity.get_reward()

            self.remove_scene_element(edible_entity)
            completely_eaten = edible_entity.eats()

            if not completely_eaten:
                self.add_scene_element(edible_entity, keep_position=True)

            body_part.is_eating = False

        return True

    def _agent_teleports(self, arbiter, space, data):

        agent = self._get_agent_from_shape(arbiter.shapes[0])
        teleport = self._get_scene_element_from_shape(arbiter.shapes[1])

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
                    width_length=[width+2, length+2],
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

        self.add_interaction(CollisionTypes.AGENT, CollisionTypes.GRASPABLE, self._agent_grasps)
        self.add_interaction(CollisionTypes.AGENT, CollisionTypes.CONTACT, self._agent_touches_entity)
        self.add_interaction(CollisionTypes.AGENT, CollisionTypes.EDIBLE, self._agent_eats)
        self.add_interaction(CollisionTypes.AGENT, CollisionTypes.INTERACTIVE, self._agent_interacts)
        self.add_interaction(CollisionTypes.AGENT, CollisionTypes.PASSIVE, self._agent_enters_zone)
        self.add_interaction(CollisionTypes.GEM, CollisionTypes.ACTIVATED_BY_GEM, self._gem_interacts)
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

    playgrounds = {}

    @classmethod
    def register(cls, playground_group, playground_name):
        """
        Registers a playground
        """
        def decorator(subclass):

            if playground_group not in cls.playgrounds:
                cls.playgrounds[playground_group] = {}

            if playground_name in cls.playgrounds[playground_group]:
                raise ValueError(playground_name+' already registered')

            cls.playgrounds[playground_group][playground_name] = subclass
            return subclass

        return decorator
