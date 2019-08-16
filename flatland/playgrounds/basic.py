import pymunk, pygame
import pymunk.pygame_util
from pygame.color import THECOLORS

from flatland import scenes as  scenes
from flatland.entities import basic, yielder, actionable
from flatland.utils.config import *

from flatland.playgrounds.register import PlaygroundGenerator

from ..common.default_scene_parameters import *

import random


@PlaygroundGenerator.register_subclass('basic')
class BasicEmptyPlayground(object):#TODO: implement simulation steps, size_envir, multithreading


    def __init__(self , params ):

        scene_parameters = params.get('scene', {})
        scene_parameters = {**basic_scene_default, **scene_parameters}

        self.scene = self.generateScene( scene_parameters )

        self.width, self.height = self.scene.total_area


        # Initialization of the pymunk space, this space is responsible for modelling all the physics
        self.space = pymunk.Space()
        self.space.gravity = pymunk.Vec2d(0., 0.)
        self.space.collision_bias = 0
        self.space.collision_persistence = 1
        self.space.collision_slop = 0
        self.space.damping = SPACE_DAMPING

        # Data structures to save list of entities, and relations between them
        # TODO: better data structure, with classes
        self.physical_entities = {}
        self.yielders = {}

        # Screen for display
        #self.screen = pygame.display.set_mode((self.width, self.height))
        #self.screen.set_alpha(None)
        self.screen = pygame.Surface((self.width, self.height))

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
        self.grasped = []
        self.timers = {}
        self.agents = []

        for elem in self.scene.elements:
            self.addEntity( elem , add_to_basics = False)

        if 'entities' in params:
            for ent in params['entities']:
                self.addEntity(ent)



    def generateScene(self, scene_params):

        scene_type = scene_params['scene_type']
        return scenes.SceneGenerator.create( scene_type , scene_params)

    def addAgent(self, ag):

        self.agents.append(ag)

    def addEntity(self, entity_params, add_to_basics = True):
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
            self.space.add(new_entity.body_sensor, new_entity.shape_sensor)
            self.space.add(new_entity.body_body, new_entity.shape_body)

            actionable_type =  new_entity.actionable_type

            id = new_entity.name_id

            if actionable_type == 'distractor':
                self.relations['actionables']['distractors'].append(id)

            elif actionable_type == 'edible':
                self.relations['actionables']['edibles'].append(id)

            elif actionable_type == 'dispenser':
                self.relations['actionables']['dispensers'][id] = []

            elif actionable_type == 'door':
                id_door = self.addEntity(new_entity.door_params)
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
            self.space.add(new_entity.body_body, new_entity.shape_body)


        else:
            new_entity = basic.BasicObject(entity_params)
            id = new_entity.name_id

            if add_to_basics: self.relations['basics'].append(id)

            self.space.add(new_entity.body_body, new_entity.shape_body)

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
        self.screen.fill(THECOLORS["black"])
        self.draw()
        self.draw_activation_radius()

        imgdata = pygame.surfarray.array3d( self.screen )
        return imgdata

    def generate_playground_image_sensor(self):
        # Update the screen of the environment
        self.screen.fill(THECOLORS["black"])
        self.draw()

        imgdata = pygame.surfarray.array3d( self.screen )
        return imgdata

    def draw(self):

        for id_entity in self.physical_entities:

            if self.physical_entities[id_entity].visible:
                self.physical_entities[id_entity].draw(self.screen)

        for ag in self.agents:

            ag.draw(self.screen)

    def draw_activation_radius(self):

        for id_entity in self.physical_entities:

            if self.physical_entities[id_entity].activable:

                self.physical_entities[id_entity].draw_activation_radius(self.screen)
                self.physical_entities[id_entity].draw(self.screen)



    def initialize_textures(self):

        #for id_entity in self.physical_entities:

        #    self.physical_entities[id_entity].initialize_texture()

        for ag in self.agents:

            ag.draw(self.screen)

    def yielders_produce(self):

        for yielder_id in self.relations['yielders']:

            if (random.random() < self.yielders[yielder_id].probability) and (len(self.relations['yielders'][yielder_id]) < self.yielders[yielder_id].limit):
                new_obj = self.yielders[yielder_id].produce()
                id_obj = self.addEntity(new_obj, add_to_basics=False)
                self.relations['yielders'][yielder_id].append(id_obj)

    def check_timers(self):

        for door_opener_id in self.timers.copy().keys():
            self.timers[door_opener_id] -= 1

            if self.timers[door_opener_id] < 0:
                door_id = self.relations['actionables']['doors'][door_opener_id]
                door = self.physical_entities[door_id]
                door_opener = self.physical_entities[door_opener_id]

                self.space.add(door.body_body, door.shape_body)
                door_opener.door_closed = True
                door.visible = True

                # TODO: change
                self.timers.pop(door_opener_id)

    def release_grasps(self):

        for agent in self.agents:

            if agent.is_holding == False:

                for joint in agent.grasped:
                    self.space.remove(joint)
                agent.grasped = []