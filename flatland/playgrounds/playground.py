import pymunk, pygame
import pymunk.pygame_util
from pygame.color import THECOLORS

from flatland import scenes as  scenes
from flatland.entities import basic, yielder, actionable
from flatland.utils.config import *

from ..default_parameters.scenes import *

import random

import time


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
    def create(cls, playground_name, params = {}):

        if playground_name not in cls.subclasses:
            raise ValueError('Playground not implemented:' + playground_name)

        return cls.subclasses[playground_name](params)

class Playground():

    def __init__(self, params ):

        # Generate Scene
        scene_parameters = params.get('scene', {})
        scene_parameters = {**basic_scene_default, **scene_parameters}
        self.scene = self.generate_scene(scene_parameters)
        self.width, self.height = self.scene.total_area

        # Initialization of the pymunk space, this space is responsible for modelling all the physics
        self.space = None
        self.initialize_space()

        # Screen for display
        self.topdown_view = pygame.Surface((self.width, self.height))

        # Data structures to save list of entities, and relations between them

        self.physical_entities = {}
        self.yielders = {}

        self.relations = {}
        self.relations['basics'] = []
        self.relations['absorbables'] = []
        self.relations['actionables'] = { 'doors': {},
                                          'edibles': [],
                                          'distractors': [],
                                          'dispensers': {},
                                          'graspables': []
                                          }
        self.relations['yielders'] = {}

        # Store the temporary pinjoints for grasping
        self.grasped = {}

        # Store the timers for doors or other timed events
        self.timers = {}

        for elem in self.scene.elements:
            self.add_entity(elem, add_to_basics = False)

        if 'entities' in params:
            for ent in params['entities']:
                self.add_entity(ent)

        # TODO: Replace by class for registring, and import all collisions in a separate file
        self.handle_collisions()

        #self.initialize_textures()

        self.agents = []
        self.body_parts_agents = {}

        self.has_reached_termination = False



    def initialize_space(self):

        self.space = pymunk.Space()
        self.space.gravity = pymunk.Vec2d(0., 0.)
        #self.space.collision_bias = 0
        self.space.collision_persistence = 1
        self.space.collision_slop = 0
        self.space.damping = SPACE_DAMPING

    def update_playground(self):

        self.yielders_produce()
        self.check_timers()
        self.release_grasps()

    def generate_scene(self, scene_params):

        scene_type = scene_params['scene_type']
        return scenes.SceneGenerator.create( scene_type , scene_params)

    def add_agent(self, agent):

        self.agents.append( agent )

        # Todo: replace by function to get coordinates
        if agent.starting_position['type'] == 'fixed':

            pos = agent.starting_position['position']

        for part_name, part in agent.frame.anatomy.items():

            if part.body is not None:

                part.body.position = pos[:2]
                part.body.angle = pos[2]
                self.space.add(part.body)

            if part.shape is not None:
                self.space.add(part.shape)

            if part.joint is not None:
                for j in part.joint:
                    # self.playground.space.add(part.joint)
                    self.space.add(j)

            self.body_parts_agents[part.shape] = agent

    def add_entity(self, entity_params, add_to_basics = True):
        '''
        Create new entity and assign  it to corresponding dictionary
        Different dictionaries to deal with different logics

        :param entity_params: dictionary representing parameters of an entity. Human readable format.
        :return:
        '''

        # Create new entity, give it an id then add it to  list entities
        entity_type = entity_params.get('entity_type', False)

        #id = str(self.index_entities)
        # TODO: Class entity with counter / id
        #self.index_entities += 1
        # Add entity in relational data structure, and get shapes

        if entity_type == 'actionable' :

            new_entity = actionable.ActionableGenerator.create(entity_params)

            # TODO: verify that we need 2 steps and 2 pairs shape/body
            self.space.add(new_entity.pm_body, new_entity.pm_shape, new_entity.pm_sensor)

            actionable_type =  new_entity.actionable_type

            id = new_entity.name_id

            if actionable_type == 'distractor':
                self.relations['actionables']['distractors'].append(id)

            elif actionable_type == 'edible':
                self.relations['actionables']['edibles'].append(id)

            elif actionable_type == 'dispenser':
                self.relations['actionables']['dispensers'][id] = []

            elif actionable_type == 'door':
                id_door = self.add_entity(new_entity.door_params)
                self.relations['actionables']['doors'][id] = id_door

            elif actionable_type == 'graspable':

                self.relations['actionables']['graspables'].append( id)
            # TODO: test exception
            else:
                raise ValueError('actionable type {} not implemented'.format(actionable_type) )

        elif entity_type == 'yielder':
            new_entity = yielder.YielderObject(entity_params)
            id = new_entity.name_id
            self.relations['yielders'][id] = []

        elif entity_type == 'absorbable':
            new_entity = basic.BasicObject(entity_params)
            id = new_entity.name_id
            self.space.add(new_entity.pm_body, new_entity.pm_shape)


        else:
            new_entity = basic.BasicObject(entity_params)
            id = new_entity.name_id

            if add_to_basics: self.relations['basics'].append(id)

            self.space.add(new_entity.pm_body, new_entity.pm_shape)

        if entity_type == 'yielder':
            self.yielders[id] = new_entity
        else:
            self.physical_entities[id] = new_entity

        return id

    def reset(self):
        # Reset the environment
        self.__init__(**self.parameters)

    def generate_playground_image(self):
        # Update the screen of the environment
        self.topdown_view.fill(THECOLORS["black"])
        self.draw()
        self.draw_activation_radius()

        imgdata = pygame.surfarray.array3d(self.topdown_view)
        return imgdata

    def generate_playground_image_sensor(self):
        # Update the screen of the environment

        self.topdown_view.fill(THECOLORS["black"])
        self.draw()

        imgdata = pygame.surfarray.array3d(self.topdown_view)

        return imgdata

    def draw(self):

        for id_entity in self.physical_entities:

            if self.physical_entities[id_entity].visible:
                self.physical_entities[id_entity].draw(self.topdown_view)

        for agent in self.agents:

            agent.frame.draw(self.topdown_view)

    def draw_activation_radius(self):

        for id_entity in self.physical_entities:

            if self.physical_entities[id_entity].activable:

                self.physical_entities[id_entity].draw_activation_radius(self.topdown_view)
                self.physical_entities[id_entity].draw(self.topdown_view)

    def yielders_produce(self):

        for yielder_id in self.relations['yielders']:

            if (random.random() < self.yielders[yielder_id].probability) and (len(self.relations['yielders'][yielder_id]) < self.yielders[yielder_id].limit):
                new_obj = self.yielders[yielder_id].produce()
                id_obj = self.add_entity(new_obj, add_to_basics=False)
                self.relations['yielders'][yielder_id].append(id_obj)

    def check_timers(self):

        for door_opener_id in self.timers.copy().keys():
            self.timers[door_opener_id] -= 1

            if self.timers[door_opener_id] < 0:
                door_id = self.relations['actionables']['doors'][door_opener_id]
                door = self.physical_entities[door_id]
                door_opener = self.physical_entities[door_opener_id]

                self.space.add(door.pm_body, door.pm_shape)
                door_opener.door_closed = True
                door.visible = True

                # TODO: change
                self.timers.pop(door_opener_id)

    def release_grasps(self):

        for agent in self.agents:

            if not agent.is_holding:

                for joint in agent.grasped:
                    self.space.remove(joint)
                agent.grasped = []

    def agent_absorbs(self, arbiter, space, data):

        absorbable_shape = arbiter.shapes[1]
        agent_shape = arbiter.shapes[0]

        agent = self.body_parts_agents[agent_shape]

        absorbable_id = [id for id in self.physical_entities if self.physical_entities[id].pm_shape == absorbable_shape][0]
        absorbable = self.physical_entities[absorbable_id]

        reward = absorbable.reward

        self.space.remove(absorbable.pm_body, absorbable.pm_shape)
        self.physical_entities.pop(absorbable_id)
        if absorbable_id in self.relations['basics']:
            self.relations['basics'].remove(absorbable_id)

        # TODO: also if yielder

        for disp_id, disp_contain in self.relations['yielders'].items():
            if absorbable_id in disp_contain:
                disp_contain.remove(absorbable_id)

        for disp_id, disp_contain in self.relations['actionables']['dispensers'].items():
            if absorbable_id in disp_contain:
                disp_contain.remove(absorbable_id)


        # TODO: add reward and reset to zero at each ts
        agent.reward = reward
        agent.health += reward

        return True


    def agent_activates(self, arbiter, space, data):


        activable_shape = arbiter.shapes[1]

        agent_shape = arbiter.shapes[0]
        agent = self.body_parts_agents[agent_shape]

        is_activating = agent.is_activating

        all_activables =  list(self.relations['actionables']['doors'].keys()) + list(self.relations['actionables']['distractors']) + list(self.relations['actionables']['dispensers'].keys())

        activable_id = [id for id in all_activables if self.physical_entities[id].pm_sensor == activable_shape][0]
        activable = self.physical_entities[activable_id]

        if is_activating:

            agent.is_activating = False



            if activable.actionable_type == 'dispenser':


                if len(self.relations['actionables']['dispensers'][activable_id]) < activable.limit:
                    new_obj = activable.actionate()
                    id_new_object = self.add_entity(new_obj, add_to_basics = False)
                    self.relations['actionables']['dispensers'][activable_id].append(id_new_object)

            elif activable.actionable_type == 'door':

                if activable.door_closed:
                    activable.door_closed = False


                    door_id = self.relations['actionables']['doors'][activable_id]
                    door = self.physical_entities[door_id]

                    space.remove(door.pm_body, door.pm_shape)
                    door.visible = False

                    self.timers[activable_id] = activable.time_open



            else:
                activable.actionate()

        return True

    def agent_grasps(self, arbiter, space, data):

        agent_shape = arbiter.shapes[0]
        agent = self.body_parts_agents[agent_shape]

        activable_shape = arbiter.shapes[1]

        all_activables =  list(self.relations['actionables']['graspables'])

        activable_id = [id for id in all_activables if self.physical_entities[id].pm_sensor == activable_shape][0]
        activable = self.physical_entities[activable_id]

        if agent.is_grasping and not agent.is_holding and activable.movable :

            # create new link
            agent.is_holding = True

            j1 = pymunk.PinJoint(activable.pm_body, agent.frame.anatomy['base'].body, (0,5), (0,-5))
            j2 = pymunk.PinJoint(activable.pm_body, agent.frame.anatomy['base'].body, (0,-5), (0,5))
            j3 = pymunk.PinJoint(activable.pm_body, agent.frame.anatomy['base'].body, (5,5), (0,5))
            j4 = pymunk.PinJoint(activable.pm_body, agent.frame.anatomy['base'].body, (5,-5), (0,5))

            self.space.add(j1, j2, j3, j4)

            agent.grasped.append(j1)
            agent.grasped.append(j2)
            agent.grasped.append(j3)
            agent.grasped.append(j4)

        return True



    # TODO: norm PEP8, is_eating -> b_eating ?
    def agent_eats(self, arbiter, space, data):

        agent_shape = arbiter.shapes[0]
        agent = self.body_parts_agents[agent_shape]

        is_eating = agent.is_eating

        sensor_shape = arbiter.shapes[1]
        edible_id = [id for id in self.relations['actionables']['edibles'] if self.physical_entities[id].pm_sensor == sensor_shape][0]
        edible = self.physical_entities[edible_id]

        if is_eating:

            agent.is_eating = False

            space.remove(edible.pm_body, edible.pm_shape, edible.pm_sensor)

            space.add_post_step_callback(self.eaten_shrinks, edible_id, agent )

        return True

    def eaten_shrinks(self, space, edible_id, agent):

        edible = self.physical_entities[edible_id]
        edible.actionate()

        agent.reward += edible.reward

        if edible.radius > 5 :

            space.add(edible.pm_body, edible.pm_shape, edible.pm_sensor)


        else:
            self.physical_entities.pop(edible_id)
            self.relations['actionables']['edibles'].remove(edible_id)

        return True

    def handle_collisions(self):

        # Collision handlers
        h_abs = self.space.add_collision_handler(collision_types['agent'], collision_types['absorbable'])
        h_abs.pre_solve = self.agent_absorbs

        h_act = self.space.add_collision_handler(collision_types['agent'], collision_types['activable'])
        h_act.pre_solve = self.agent_activates

        h_edible = self.space.add_collision_handler(collision_types['agent'], collision_types['edible'])
        h_edible.pre_solve = self.agent_eats

        h_grasps = self.space.add_collision_handler(collision_types['agent'], collision_types['graspable'])
        h_grasps.pre_solve = self.agent_grasps
