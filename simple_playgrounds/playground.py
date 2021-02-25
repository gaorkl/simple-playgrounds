# -*- coding: utf-8 -*-
""" Playground documentation.

Module defining Playground Base Class

"""

import os
from abc import ABC
import yaml
import pymunk


from .utils import PositionAreaSampler
from .utils.definitions import SPACE_DAMPING, CollisionTypes, SceneElementTypes

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
        initial_agent_position: position or PositionAreaSampler,
            Starting position of an agent (single agent).
        done: bool, True if the playground reached termination.

    Notes:
          In the case of multi-agent setting, individual initial positions can be defined when
          instantiating the playground.
    """

    # pylint: disable=too-many-instance-attributes

    time_limit = None
    _scene_entities = []
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

        # Add entities declared in the scene
        for scene_entity in self._scene_entities:
            self.add_scene_element(scene_entity)

        self.done = False
        self.initial_agent_position = None

        self._handle_interactions()

    @staticmethod
    def parse_configuration(key):
        """ Private method that parses yaml configuration files.

        Args:
            key: (str) name of the playground configuration.

        Returns:
            Dictionary of attributes and default values.

        """

        fname = 'utils/configs/playground.yml'

        __location__ = os.path.realpath(os.path.join(os.getcwd(), os.path.dirname(__file__)))
        with open(os.path.join(__location__, fname), 'r') as yaml_file:
            default_config = yaml.load(yaml_file, Loader=yaml.FullLoader)

        return default_config[key]

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
        """ Reset the Playground to its initial state.

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
            self.remove_agent(agent)
            self.add_agent(agent)

        self.done = False

    def add_agent(self, agent,
                  allow_overlapping=True,
                  max_attempts=100,
                  error_if_fails=True,
                  keep_position=False):
        """ Method to add an Agent to the Playground.

        Args:
            agent: Agent to add to the Playground
            allow_overlapping: If True, allows new agent to overlap with other elements when added to the Playground.
            max_attempts: If overlapping is not allowed, maximum number of attempts to place the agent.
            error_if_fails: If True, an error will be raised if agent can't be placed in the Playground.
            keep_position: if True, will not reinitialize position.

        Notes:
            keep_position is useful in the case where agent must disappear and reappear in the same position.
            In this case, the position should not be re-initialized.

        """

        # If already there
        if agent in self.agents:
            raise ValueError('Agent already in Playground')

        # Inform agent of the playground size
        agent.size_playground = self.size

        # Set initial position
        if agent.initial_position is not None:
            pass
        elif self.initial_agent_position is not None:
            agent.initial_position = self.initial_agent_position
        else:
            raise ValueError("""Agent initial position should be defined in the playground or passed as an argument)
                             to the class agent""")

        # Place agent in environment
        if allow_overlapping:
            self._add_agent(agent, keep_position)

        else:
            attempt = 0
            success = False

            while not success or attempt < max_attempts:

                self._add_agent(agent, keep_position)
                if not self._agent_colliding(agent):
                    success = True
                else:
                    self.remove_agent(agent)
                attempt += 1

            if not success:

                msg = 'Agent could not be placed without overlapping'

                if error_if_fails:
                    raise ValueError(msg)

                else:
                    print(msg)

    def _add_agent(self, agent, keep_position):
        """ Add an agent to the playground.

        Args:
            agent: Agent.

        """

        self.agents.append(agent)

        if not keep_position:
            agent.position = agent.initial_position

        for body_part in agent.parts:
            self.space.add(*body_part.pm_elements)

    def _agent_colliding(self, agent):

        all_agents_collision_shapes = [part.pm_visible_shape for part in agent.parts
                                       if part.pm_visible_shape is not None]

        all_colliding_shapes = [shape for shape in self.space.shapes.copy()
                                if not shape.sensor
                                and shape not in all_agents_collision_shapes]

        collides = False

        for part in agent.parts:

            if part.pm_visible_shape is not None:

                collisions = [part.pm_visible_shape.shapes_collide(shape) for shape in all_colliding_shapes]
                collides = collides or any([len(collision.points) != 0 for collision in collisions])

        return collides

    def add_scene_element(self, scene_element,
                          allow_overlapping=True,
                          max_attempts=100,
                          error_if_fails=True,
                          keep_position=False):
        """ Method to add a SceneElement to the Playground.

        Args:
            scene_element: Scene Element to add to the Playground
            allow_overlapping: If True, allows new elements to overlap with other elements when added to the Playground.
            max_attempts: If overlapping is not allowed, maximum number of attempts to place the element.
            error_if_fails: If True, an error will be raised if an element can't be placed in the Playground.
            keep_position: if True, will not reinitialize position

        Notes:
            keep_position is usefull in the case where scene elements must disappear and reappear in the same position.
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

            # Else
            scene_element.size_playground = self.size

            if scene_element.background or allow_overlapping:
                self._add_scene_element(scene_element, keep_position)

            else:

                attempt = 0
                success = False

                while not success or attempt < max_attempts:

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

                    else:
                        print(msg)

    def _add_scene_element(self, new_scene_element, keep_position):

        if new_scene_element in self.scene_elements:
            raise ValueError('Scene element already in Playground')

        if not keep_position:
            new_scene_element.position = new_scene_element.initial_position

        self.space.add(*new_scene_element.pm_elements)
        self.scene_elements.append(new_scene_element)
        if new_scene_element in self._disappeared_scene_elements:
            self._disappeared_scene_elements.remove(new_scene_element)

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

        if agent not in self.agents:
            return False

        for part in agent.parts:
            self.space.remove(*part.pm_elements)
            part.velocity = [0, 0, 0]
            part.grasped = []

        agent.initial_position = None

        self.agents.remove(agent)

        return True

    def remove_scene_element(self, scene_element):

        if scene_element not in self.scene_elements:
            return False

        self.space.remove(*scene_element.pm_elements)
        self.scene_elements.remove(scene_element)

        if not scene_element.is_temporary_entity:
            self._disappeared_scene_elements.append(scene_element)

        for elem in self.scene_elements:
            if elem.entity_type == 'dispenser' and scene_element in elem.produced_entities:
                elem.produced_entities.remove(scene_element)

        for field in self.fields:
            if scene_element in field.produced_entities:
                field.produced_entities.remove(scene_element)

        if scene_element in self._grasped_scene_elements.keys():
            body_part = self._grasped_scene_elements[scene_element]
            self.space.remove(*body_part.grasped)
            body_part.grasped = []
            # self._grasped_scene_elements.pop(scene_element)

        return True

    def _fields_produce(self):

        for field in self.fields:

            if field.can_produce():
                new_entity = field.produce()
                self.add_scene_element(new_entity)

    def _check_timers(self):

        for entity in self.scene_elements:

            if entity.timed and entity.timer == 0:

                list_remove, list_add = entity.activate(self)

                for entity_removed in list_remove:
                    self.remove_scene_element(entity_removed)

                for entity_added in list_add:
                    self.add_scene_element(entity_added)

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

            overlaps = self.agent_overlaps_with_element(agent, teleport)

            if not overlaps:
                self._teleported.remove((agent, teleport))

    def agent_overlaps_with_element(self, agent, element):

        overlaps = False

        for part in agent.parts:

            if element.pm_visible_shape is not None:
                overlaps = overlaps or part.pm_visible_shape.shapes_collide(element.pm_visible_shape).points

            if element.pm_interaction_shape is not None:
                overlaps = overlaps or part.pm_visible_shape.shapes_collide(element.pm_interaction_shape).points

        return overlaps

    def get_scene_element_from_shape(self, pm_shape):
        """
        Returns: Returns the Scene Element associated with the pymunk shape.

        """
        entity = next(iter([e for e in self.scene_elements if pm_shape in e.pm_elements]), None)
        return entity

    def get_agent_from_shape(self, pm_shape):
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
            pm_shape: Pymunk shaape

        Returns:
            Single entitiy or None

        """

        scene_element = self.get_scene_element_from_shape(pm_shape)
        if scene_element is not None: return scene_element

        for agent in self.agents:

            part = agent.get_bodypart_from_shape(pm_shape)
            if part is not None: return part

        return None

    def _get_closest_agent(self, ent):

        dist_list = [(a.position[0] - ent.position[0])**2 + (a.position[1] - ent.position[1])**2 for a in self.agents]
        index_min_dist = dist_list.index(min(dist_list))
        closest_agent = self.agents[index_min_dist]

        return closest_agent

    def _agent_touches_entity(self, arbiter, space, data):

        agent = self.get_agent_from_shape(arbiter.shapes[0])
        touched_entity = self.get_scene_element_from_shape(arbiter.shapes[1])

        if touched_entity is None: return True

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

        agent = self.get_agent_from_shape(arbiter.shapes[0])
        body_part = agent.get_bodypart_from_shape(arbiter.shapes[0])
        interacting_entity = self.get_scene_element_from_shape(arbiter.shapes[1])

        if interacting_entity is None: return True

        if body_part.is_activating:

            agent.reward += interacting_entity.reward

            list_remove, list_add = interacting_entity.activate(body_part)

            for entity_removed in list_remove:
                self.remove_scene_element(entity_removed)

            for entity_added in list_add:
                self.add_scene_element(entity_added)

            if interacting_entity.terminate_upon_contact:
                self.done = True

            body_part.is_activating = False

        return True

    def _agent_grasps(self, arbiter, space, data):

        agent = self.get_agent_from_shape(arbiter.shapes[0])
        body_part = agent.get_bodypart_from_shape(arbiter.shapes[0])
        interacting_entity = self.get_scene_element_from_shape(arbiter.shapes[1])

        if interacting_entity is None: return True

        if body_part.is_grasping and not body_part.is_holding:

            body_part.is_holding = True

            j_1 = pymunk.PinJoint(body_part.pm_body, interacting_entity.pm_body, (0, 5), (0, 0))
            j_2 = pymunk.PinJoint(body_part.pm_body, interacting_entity.pm_body, (0, -5), (0, 0))
            motor = pymunk.SimpleMotor(body_part.pm_body, interacting_entity.pm_body, 0)

            self.space.add(j_1, j_2, motor)  # , j_3, j_4, j_5, j_6, j_7, j_8)
            body_part.grasped = [j_1, j_2, motor]  # , j_3, j_4, j_5, j_6, j_7, j_8]

            self._grasped_scene_elements[interacting_entity] = body_part

        return True

    def _agent_enters_zone(self, arbiter, space, data):

        agent = self.get_agent_from_shape(arbiter.shapes[0])
        zone_reached = self.get_scene_element_from_shape(arbiter.shapes[1])

        if zone_reached is None: return True

        agent.reward += zone_reached.reward

        if zone_reached.terminate_upon_contact:
            self.done = True

        return True

    def _gem_interacts(self, arbiter, space, data):

        gem = self.get_scene_element_from_shape(arbiter.shapes[0])
        interacting_entity = self.get_scene_element_from_shape(arbiter.shapes[1])

        if interacting_entity is None or gem is None: return True

        agent = self._get_closest_agent(gem)
        agent.reward += interacting_entity.reward

        list_remove, list_add = interacting_entity.activate(gem)

        for entity_removed in list_remove:
            self.remove_scene_element(entity_removed)

        for entity_added in list_add:
            self.add_scene_element(entity_added)

        if interacting_entity.terminate_upon_contact:
            self.done = True

        return True

    def _agent_eats(self, arbiter, space, data):

        agent = self.get_agent_from_shape(arbiter.shapes[0])
        body_part = agent.get_bodypart_from_shape(arbiter.shapes[0])
        edible_entity = self.get_scene_element_from_shape(arbiter.shapes[1])

        if edible_entity is None: return True

        if body_part.is_eating:

            agent.reward += edible_entity.get_reward()

            self.remove_scene_element(edible_entity)
            completely_eaten = edible_entity.eats()

            if not completely_eaten:
                self.add_scene_element(edible_entity, keep_position=True)

            body_part.is_eating = False

        return True

    def _agent_teleports(self, arbiter, space, data):

        agent = self.get_agent_from_shape(arbiter.shapes[0])
        teleport = self.get_scene_element_from_shape(arbiter.shapes[1])

        if teleport is None or teleport.target is None or (agent, teleport) in self._teleported:

            return True

        if agent.is_teleporting: return True

        if teleport.target.traversable:
            agent.position = (teleport.target.position[0], teleport.target.position[1],
                              agent.position[2])
        else:
            area_shape = teleport.target.physical_shape
            if area_shape == 'rectangle':
                width = teleport.target.width + agent.base_platform.radius * 2 + 1
                length = teleport.target.length + agent.base_platform.radius * 2 + 1
                angle = teleport.target.position[-1]
                sampler = PositionAreaSampler(
                    center=[teleport.target.position[0], teleport.target.position[1]],
                    area_shape=area_shape,
                    angle=angle,
                    width_length=[width+2, length+2],
                    excl_width_length=[width, length],
                )
            else:
                radius = teleport.target.radius + agent.base_platform.radius + 1
                sampler = PositionAreaSampler(
                    center=[teleport.target.position[0], teleport.target.position[1]],
                    area_shape='circle',
                    radius=radius,
                    excl_radius=radius,
                )

            agent.position = sampler.sample()

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
    def register(cls, playground_name):
        """
        Registers a playground
        """
        def decorator(subclass):

            if playground_name in cls.playgrounds:
                raise ValueError(playground_name+' already registered')

            cls.playgrounds[playground_name] = subclass
            return subclass

        return decorator

    @classmethod
    def filter(cls, name):

        return [pg for name_pg, pg in cls.playgrounds.items() if name in name_pg]

