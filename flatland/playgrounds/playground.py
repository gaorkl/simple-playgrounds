import pymunk.pygame_util
from pygame.color import THECOLORS

from .scene_layout import SceneGenerator
from ..entities.entity import *
from ..utils.position_sampler import *
from ..utils.config import *


import random
import numpy



class PlaygroundGenerator():

    """
    Register class to provide a decorator that is used to go through the package and
    register available playgrounds.
    """

    subclasses = {}

    @classmethod
    def register_subclass(cls, playground_name):
        def decorator(subclass):
            cls.subclasses[playground_name] = subclass
            return subclass

        return decorator

    @classmethod
    def create(cls, playground_name, **scene_params):

        if playground_name not in cls.subclasses:
            raise ValueError('Playground not implemented:' + playground_name)

        return cls.subclasses[playground_name](scene_params)

class Playground():

    def __init__(self, scene_params ):

        # Generate Scene
        self.scene = self.generate_scene(scene_params)
        self.width, self.length = self.scene.width, self.scene.length

        # Initialization of the pymunk space, this space is responsible for modelling all the physics
        self.space = None
        self.initialize_space()

        # Screen for display
        self.topdown_view = pygame.Surface((self.width, self.length))
        self.topdown_entities = pygame.Surface((self.width, self.length))

        # Data structures to save list of entities, and relations between them
        self.physical_entities = []

        self.entities = []
        self.yielders = []
        self.disappeared = []

        # Store the temporary pinjoints for grasping
        self.grasped = {}

        # Store the timers for doors or other timed events
        self.timers = {}

        # Add entities declared in the scene
        for ent_params in self.scene.scene_entities:
            self.add_entity(entity_config= ent_params)

        # TODO: Replace by class for registring, and import all collisions in a separate file
        self.handle_collisions()

        self.agents = []
        self.body_parts_agents = {}

        self.has_reached_termination = False



    def initialize_space(self):

        self.space = pymunk.Space()
        self.space.gravity = pymunk.Vec2d(0., 0.)
        self.space.damping = SPACE_DAMPING

    def generate_scene(self, scene_params):

        return SceneGenerator.create( scene_params)

    def add_agent(self, agent):

        self.agents.append(agent)
        self.place_agent_in_playground(agent)

    def place_agent_in_playground(self, agent, position = None):

        agent.size_playground = self.width, self.length

        if position is None:

            position = generate_position(agent.starting_position)

        agent.position = position
        agent.velocity = [0,0,0]

        for part_name, part in agent.frame.anatomy.items():

            if part.body is not None:
                self.space.add(part.body)

            if part.shape is not None:
                self.space.add(part.shape)

            if part.joint is not None:
                for j in part.joint:
                    self.space.add(j)

    def remove_agents(self):

        for agent in self.agents:

            for part_name, part in agent.frame.anatomy.items():

                if part.body is not None:
                    self.space.remove(part.body)
                    part.body.position = [0,0]
                    part.body.angle = 0
                    part.body.velocity = (0, 0)
                    part.body.angular_velocity = 0

                if part.shape is not None:
                    self.space.remove(part.shape)

                if part.joint is not None:
                    for j in part.joint:
                        # self.playground.space.add(part.joint)
                        self.space.remove(j)

        self.agents = []



    def add_entity(self, entity_type = None, entity_config = None, **params):

        '''
        Create a new entity and adds it to space, and to the different entity lists
        :param entity_type: type of entity (dispenser, edible, absorbable...)
        :param user_config: dictionary, additional configuration provided by the user. Will overwrite default config
        :param params: any other parameters set by the users. Will overwrite user config
        :return: the new entity
        '''


        if entity_config == None:
            entity_config = {}

        entity_params = {**entity_config, **params}


        # TODO: clean :
        new_entity = EntityGenerator.create(entity_type, entity_params)

        new_entity.size_playground = [self.width, self.length]

        new_entity.position = new_entity.get_initial_position()

        if new_entity.entity_type is 'yielder':
            self.yielders.append(new_entity)

        else:


            self.space.add(*new_entity.pm_elements)
            self.entities.append(new_entity)

            if new_entity.entity_type in ['button_door_openclose', 'button_door_opentimer' ]:
                new_entity.door = self.add_entity(new_entity.door_params)

            elif new_entity.entity_type is 'lock_key_door':
                new_entity.door = self.add_entity(new_entity.door_params)
                new_entity.key = self.add_entity(new_entity.key_params)

            elif new_entity.entity_type is 'chest':
                new_entity.key = self.add_entity(new_entity.key_params)

        return new_entity


    def update_playground(self):

        for entity in self.entities:
            entity.update()
            entity.pre_step()

        self.yielders_produce()
        self.check_timers()
        self.release_grasps()

        #for entity in self.entities:

        #    entity.pre_step()

    def reset(self):
        # Reset the environment

        # Remove entities not in initial definition of environments
        # Reset entities which are in environment initialization

        print('reset playground')

        for entity in self.entities.copy():

            self.space.remove(*entity.pm_elements)

            replace = entity.reset()

            if replace:
                self.space.add(*entity.pm_elements)
            else:
                self.entities.remove(entity)


        for entity in self.disappeared.copy():

            replace = entity.reset()

            if replace:
                self.space.add(*entity.pm_elements)

                self.disappeared.remove(entity)
                self.entities.append(entity)

            else:
                self.disappeared.remove(entity)

        for entity in self.yielders:
            entity.reset()

        # Reset flags and counters
        self.grasped = {}
        self.timers = {}
        self.has_reached_termination = False


    def generate_entities_image(self, draw_interaction = False):

        # Update the screen of the environment
        self.topdown_entities.fill(THECOLORS["black"])

        for entity in self.entities:
            entity.draw(self.topdown_entities, draw_interaction)


    def generate_agent_image(self, sensor_agent):

        agent_image = self.topdown_entities.copy()

        for agent in self.agents:
            #if agent is not sensor_agent:
            if agent is not sensor_agent:
                agent.frame.draw(agent_image, visible_to_self=False)
            else:
                agent.frame.draw(agent_image, visible_to_self=True)

        imgdata = pygame.surfarray.array3d(agent_image)

        imgdata = numpy.rot90(imgdata, 1, (1,0))
        imgdata = imgdata[::-1, :, ::-1]

        return imgdata



    def generate_playground_image(self, draw_interaction = False, sensor_agent = None):
        # Update the screen of the environment
        self.topdown_view.fill(THECOLORS["black"])

        for entity in self.entities:
            entity.draw(self.topdown_view, draw_interaction)

        for agent in self.agents:
            #if agent is not sensor_agent:
            if agent is not sensor_agent:
                agent.frame.draw(self.topdown_view, visible_to_self=False)
            else:
                agent.frame.draw(self.topdown_view, visible_to_self=True)
            """else:
                #import pdb;pdb.set_trace()
                body_parts = agent.frame.anatomy.keys()
                for part in body_parts:
                    #if part.self_visible:
                    if part == 'arm1_2':
                        agent.frame.anatomy[part].draw(self.topdown_view, visible_to_self=True)"""

        imgdata = pygame.surfarray.array3d(self.topdown_view)

        imgdata = numpy.rot90(imgdata, 1, (1,0))
        imgdata = imgdata[::-1, :, ::-1]

        return imgdata


    def yielders_produce(self):

        for yielder in self.yielders:

            if (random.random() < yielder.probability) and ( len(yielder.yielded_elements) < yielder.limit):
                new_obj_params = yielder.produce()
                new_obj = self.add_entity(new_obj_params, is_temporary_entity=True)
                yielder.yielded_elements.append(new_obj)

    def check_timers(self):

        for entity in self.entities:

            if entity.entity_type == 'button_door_opentimer' and entity.timer == 0 :
                self.space.add(*entity.door.pm_elements)
                self.entities.append(entity.door)
                self.disappeared.remove(entity.door)
                entity.close_door()

    def release_grasps(self):

        for agent in self.agents:

            if not agent.is_holding:

                for joint in agent.grasped:
                    self.space.remove(joint)
                agent.grasped = []

    def get_entity_from_visible_shape(self, pm_shape):

        entity = [entity for entity in self.entities if entity.pm_visible_shape == pm_shape][0]
        return entity

    def get_agent_from_shape(self, pm_shape):

        for agent in self.agents:

            if agent.owns_shape(pm_shape):

                return agent

    def agent_touches_entity(self, arbiter, space, data):

        agent = self.get_agent_from_shape(arbiter.shapes[0])
        touched_entity = self.get_entity_from_visible_shape(arbiter.shapes[1])

        if touched_entity.absorbable:

            reward = touched_entity.reward
            agent.reward += reward

            self.space.remove(*touched_entity.pm_elements)
            self.entities.remove(touched_entity)

            if (not touched_entity.is_temporary_entity):
                self.disappeared.append(touched_entity)


            for entity in self.entities:
                if entity.entity_type is 'dispenser' and touched_entity in entity.produced_elements:
                    entity.produced_elements.remove(touched_entity)

            for entity in self.yielders:
                if touched_entity in entity.yielded_elements:
                    entity.yielded_elements.remove(touched_entity)

        elif touched_entity.entity_type in 'contact_endzone':
            self.has_reached_termination = True
            reward = touched_entity.get_reward()
            agent.reward += reward

        return True


    def agent_interacts(self, arbiter, space, data):

        agent = self.get_agent_from_shape(arbiter.shapes[0])

        # TODO: replace with this everywhere:
        interacting_entity = next( iter([entity for entity in self.entities if entity.pm_interaction_shape == arbiter.shapes[1]]), None)

        if agent.is_eating and interacting_entity.edible:

            agent.is_eating = False

            space.remove(interacting_entity.pm_body, interacting_entity.pm_visible_shape, interacting_entity.pm_interaction_shape)
            space.add_post_step_callback(self.eaten_shrinks, interacting_entity, agent )

        elif agent.is_activating and (interacting_entity.entity_type is 'dispenser'):

            agent.is_activating = False

            if len(interacting_entity.produced_elements) < interacting_entity.prodution_limit:
                new_entity_params = interacting_entity.activate()
                new_entity = self.add_entity('absorbable', new_entity_params, is_temporary_entity=True)
                interacting_entity.produced_elements.append(new_entity)

        elif agent.is_activating and (interacting_entity.entity_type is 'button_door_openclose'):

            agent.is_activating = False
            interacting_entity.activate()
            door = interacting_entity.door

            if interacting_entity.door_opened:
                space.remove(*door.pm_elements)
                self.entities.remove(door)
                self.disappeared.append(door)
            else:
                space.add(*door.pm_elements)
                self.entities.append(door)
                self.disappeared.remove(door)

        elif agent.is_activating and (interacting_entity.entity_type is 'button_door_opentimer'):

            interacting_entity.activate()
            door = interacting_entity.door

            if not interacting_entity.door_opened :
                space.remove(*door.pm_elements)
                self.entities.remove(door)
                self.disappeared.append(door)
                interacting_entity.door_opened = True



        elif agent.is_grasping and not agent.is_holding and interacting_entity.movable :

            agent.is_holding = True

            j1 = pymunk.PinJoint(interacting_entity.pm_body, agent.frame.anatomy['base'].body, (0,5), (0,-5))
            j2 = pymunk.PinJoint(interacting_entity.pm_body, agent.frame.anatomy['base'].body, (0,-5), (0,5))
            j3 = pymunk.PinJoint(interacting_entity.pm_body, agent.frame.anatomy['base'].body, (5,5), (0,5))
            j4 = pymunk.PinJoint(interacting_entity.pm_body, agent.frame.anatomy['base'].body, (5,-5), (0,5))

            self.space.add(j1, j2, j3, j4)
            agent.grasped += [j1, j2, j3, j4]

        return True

    def eaten_shrinks(self, space, edible, agent):

        edible.activate()

        agent.reward += edible.reward

        if edible.reward > edible.min_reward :

            space.add(*edible.pm_elements)

        else:
            if not edible.is_temporary_entity:
                self.disappeared.append(edible)
            self.entities.remove(edible)

        return True

    def agent_enters_zone(self, arbiter, space, data):

        agent = self.get_agent_from_shape(arbiter.shapes[0])
        zone_reached = [entity for entity in self.entities if entity.pm_interaction_shape == arbiter.shapes[1]][0]

        if zone_reached.entity_type == 'end_zone':
            self.has_reached_termination = True
            reward = zone_reached.get_reward()
            agent.reward += reward

        elif zone_reached.entity_type in ['reward_zone', 'fireball', 'fairy' ]:
            reward = zone_reached.get_reward()
            agent.reward += reward

        else:
            pass

        # agent.reward += termination_reward
        # agent.health += termination reward

        return True

    def gem_interacts(self, arbiter, space, data):

        gem = [entity for entity in self.entities if entity.pm_visible_shape == arbiter.shapes[0]][0]
        interacting_entity = [entity for entity in self.entities if entity.pm_interaction_shape == arbiter.shapes[1]][0]

        if interacting_entity.entity_type is 'lock_key_door' and gem is interacting_entity.key :
            interacting_entity.activate()
            interacting_entity.door_opened = True

            door = interacting_entity.door
            space.remove(*door.pm_elements)

            space.remove(*gem.pm_elements)

            self.entities.remove(door)
            self.entities.remove(gem)

            self.disappeared.append(door)
            self.disappeared.append(gem)

        if interacting_entity.entity_type is 'chest' and gem is interacting_entity.key :
            reward = interacting_entity.get_reward()
            space.remove(*gem.pm_elements)
            self.entities.remove(gem)
            self.disappeared.append(gem)
            interacting_entity.reward_provided = True


            # to be changed when multiagents with competition: only closest agent should have reward
            for agent in self.agents:
                agent.reward += reward



        return True



    def handle_collisions(self):

        # TODO: replace all collisoin handlers with:
        # - agent agent
        # - agent interactive
        # - interactive interactive

        # Collision handlers
        h_touch = self.space.add_collision_handler(collision_types['agent'], collision_types['contact'])
        h_touch.pre_solve = self.agent_touches_entity

        h_interact = self.space.add_collision_handler(collision_types['agent'], collision_types['interactive'])
        h_interact.pre_solve = self.agent_interacts

        h_zone = self.space.add_collision_handler(collision_types['agent'], collision_types['zone'])
        h_zone.pre_solve = self.agent_enters_zone

        # Collision with gems
        h_gem_interactive = self.space.add_collision_handler(collision_types['gem'], collision_types['interactive'])
        h_gem_interactive.pre_solve = self.gem_interacts
