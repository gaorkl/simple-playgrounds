import pymunk.pygame_util
from pygame.color import THECOLORS

from .scene_layout import SceneGenerator
from flatland.entities.entity import *
from flatland.utils.game_utils import *
from flatland.utils.config import *

from ..default_parameters.scenes import *

import random, numpy


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
    def create(cls, playground_params):

        playground_name = playground_params['playground_type']

        if playground_name not in cls.subclasses:
            raise ValueError('Playground not implemented:' + playground_name)

        return cls.subclasses[playground_name](playground_params)


class Playground():

    def __init__(self, params ):

        # Save params in case of reset
        self.params = params

        # Generate Scene
        scene_parameters = params.get('scene', {})
        scene_parameters = {**room_scene_default, **scene_parameters}

        self.scene = self.generate_scene(scene_parameters)
        self.width, self.length = self.scene.width, self.scene.length

        # Initialization of the pymunk space, this space is responsible for modelling all the physics
        self.space = None
        self.initialize_space()

        # Screen for display
        self.topdown_view = pygame.Surface((self.width, self.length))

        # Data structures to save list of entities, and relations between them
        self.physical_entities = []

        self.entities = []
        self.basics = []
        self.absorbables = []
        self.actionables = []
        self.yielders = []
        self.zones = []

        # Store the temporary pinjoints for grasping
        self.grasped = {}

        # Store the timers for doors or other timed events
        self.timers = {}

        # Add entities declared in the scene
        for elem in self.scene.entity_parameters:
            self.add_entity(elem)

        # Add entities declared in the Playground
        if 'entities' in params:
            for ent in params['entities']:
                self.add_entity(ent)

        # TODO: Replace by class for registring, and import all collisions in a separate file
        self.handle_collisions()

        self.agents = []
        self.body_parts_agents = {}

        self.has_reached_termination = False

        self.starting_position = {
            'type': 'rectangle',
            'x_range': [self.width / 2.0 - 15, self.width / 2.0 + 15],
            'y_range': [self.length / 2.0 - 15, self.length / 2.0 + 15],
            'angle_range': [0, 3.14 * 2],
        }

    def initialize_space(self):

        self.space = pymunk.Space()
        self.space.gravity = pymunk.Vec2d(0., 0.)
        #self.space.collision_persistence = 1
        #self.space.collision_slop = 0.001
        #self.space.collision_bias = 0.001
        self.space.damping = SPACE_DAMPING

    def generate_scene(self, scene_params):

        return SceneGenerator.create( scene_params)

    def add_agent(self, agent):

        self.agents.append(agent)

        starting_position = generate_position(self.starting_position)

        for part_name, part in agent.frame.anatomy.items():

            if part.body is not None:

                part.body.position = [ starting_position[0] + part.body.position[0], starting_position[1] + part.body.position[1]]
                part.body.angle = starting_position[2] + part.body.angle
                self.space.add(part.body)

            if part.shape is not None:
                self.space.add(part.shape)

            if part.joint is not None:
                for j in part.joint:
                    # self.playground.space.add(part.joint)
                    self.space.add(j)

    def remove_agents(self):

        for agent in self.agents:

            for part_name, part in agent.frame.anatomy.items():

                if part.body is not None:
                    self.space.remove(part.body)
                    part.body.velocity = (0,0)
                    part.body.angular_velocity = 0

                if part.shape is not None:
                    self.space.remove(part.shape)

                if part.joint is not None:
                    for j in part.joint:
                        # self.playground.space.add(part.joint)
                        self.space.remove(j)


    def add_entity(self, entity_params, add_to_basics = True):
        '''
        Create new entity and assign  it to corresponding dictionary
        Different dictionaries to deal with different logics

        :param entity_params: dictionary representing parameters of an entity. Human readable format.
        :return:
        '''

        # Create new entity, add it to space
        new_entity = EntityGenerator.create(entity_params)

        if new_entity.entity_type is 'yielder':
            self.yielders.append(new_entity)

        else:
            self.space.add(new_entity.pm_elements)
            self.entities.append(new_entity)

            if new_entity.entity_type in ['button_door_openclose', 'button_door_opentimer' ]:
                new_entity.door = self.add_entity(new_entity.door_params)

            elif new_entity.entity_type is 'lock_key_door':
                new_entity.door = self.add_entity(new_entity.door_params)
                new_entity.key = self.add_entity(new_entity.key_params)

        return new_entity

    def update_playground(self):

        for entity in self.entities:
            entity.update()

        self.yielders_produce()
        self.check_timers()
        self.release_grasps()

        #for entity in self.entities:

        #    entity.pre_step()

    def reset(self):
        # Reset the environment
        self.__init__(self.params)

    def generate_playground_image(self, draw_interaction = False, carthesian_view = False, sensor_agent = None):
        # Update the screen of the environment
        self.topdown_view.fill(THECOLORS["black"])

        for entity in self.entities:
            entity.draw(self.topdown_view, draw_interaction)

        for agent in self.agents:
            if agent is not sensor_agent:
                agent.frame.draw(self.topdown_view)

        imgdata = pygame.surfarray.array3d(self.topdown_view)

        if carthesian_view:
            imgdata = numpy.rot90(imgdata, 1, (1,0))

            return imgdata
        else:
            return imgdata




    def yielders_produce(self):

        for yielder in self.yielders:

            if (random.random() < yielder.probability) and ( len(yielder.yielded_elements) < yielder.limit):
                new_obj_params = yielder.produce()
                new_obj = self.add_entity(new_obj_params, add_to_basics=False)
                yielder.yielded_elements.append(new_obj)

    def check_timers(self):

        for entity in self.entities:

            if entity.entity_type == 'button_door_opentimer' and entity.timer == 0 :
                self.space.add(entity.door.pm_body, entity.door.pm_visible_shape)
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

            self.space.remove(touched_entity.pm_body, touched_entity.pm_visible_shape)
            self.entities.remove(touched_entity)

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

            if len(interacting_entity.produced_elements) < interacting_entity.limit:
                new_entity_params = interacting_entity.activate()
                new_entity = self.add_entity(new_entity_params)
                interacting_entity.produced_elements.append(new_entity)

        elif agent.is_activating and (interacting_entity.entity_type is 'button_door_openclose'):

            agent.is_activating = False
            interacting_entity.activate()
            door = interacting_entity.door

            if interacting_entity.door_opened:
                space.remove(door.pm_body, door.pm_visible_shape)

            else:
                space.add(door.pm_body, door.pm_visible_shape)

        elif agent.is_activating and (interacting_entity.entity_type is 'button_door_opentimer'):

            interacting_entity.activate()
            door = interacting_entity.door

            if not interacting_entity.door_opened :
                space.remove(door.pm_body, door.pm_visible_shape)
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

            space.add(edible.pm_body, edible.pm_interaction_shape, edible.pm_visible_shape)

        else:
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
            door = interacting_entity.door
            space.remove(door.pm_body, door.pm_visible_shape)
            interacting_entity.door_opened = True

            space.remove(gem.pm_body, gem.pm_visible_shape, gem.pm_interaction_shape)
            self.entities.remove(door)
            self.entities.remove(gem)

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
