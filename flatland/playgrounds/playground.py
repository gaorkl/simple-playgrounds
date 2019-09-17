import pymunk, pygame
import pymunk.pygame_util
from pygame.color import THECOLORS

from flatland import scenes as  scenes
from flatland.entities import basic, yielder, actionable, zone
from flatland.utils.game_utils import *
from flatland.utils.config import *

from ..default_parameters.scenes import *

import random


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

        # Save params in case of reset
        self.params = params

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
        self.physical_entities = []

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
        for elem in self.scene.elements:
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

    def initialize_space(self):

        self.space = pymunk.Space()
        self.space.gravity = pymunk.Vec2d(0., 0.)
        self.space.collision_persistence = 1
        self.space.collision_slop = 0
        self.space.damping = SPACE_DAMPING

    def generate_scene(self, scene_params):

        scene_type = scene_params['scene_type']
        return scenes.SceneGenerator.create( scene_type , scene_params)

    def add_agent(self, agent):

        self.agents.append(agent)

        starting_position = generate_position(agent.starting_position)

        for part_name, part in agent.frame.anatomy.items():

            if part.body is not None:

                part.body.position = starting_position[:2]
                part.body.angle = starting_position[2]
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

        # Create new entity, give it an id then add it to  list entities
        entity_type = entity_params.get('entity_type', False)

        if entity_type == 'actionable':

            new_entity = actionable.ActionableGenerator.create(entity_params)
            self.space.add(new_entity.pm_body, new_entity.pm_shape, new_entity.pm_sensor)

            self.actionables.append(new_entity)

            if new_entity.actionable_type == 'door_opener':
                door = self.add_entity(new_entity.door_params)
                new_entity.assign_door(door)

        elif entity_type == 'zone':
            new_entity = zone.ZoneGenerator.create(entity_params)
            self.space.add(new_entity.pm_body, new_entity.pm_sensor)
            self.zones.append(new_entity)

        elif entity_type == 'yielder':
            new_entity = yielder.YielderObject(entity_params)
            self.yielders.append(new_entity)

        elif entity_type == 'absorbable':
            new_entity = basic.BasicObject(entity_params)
            self.space.add(new_entity.pm_body, new_entity.pm_shape)
            self.absorbables.append(new_entity)

        else:
            new_entity = basic.BasicObject(entity_params)
            if add_to_basics: self.basics.append(new_entity)

            self.space.add(new_entity.pm_body, new_entity.pm_shape)

        if entity_type not in ['yielder', 'zone']:
            self.physical_entities.append(new_entity)

        return new_entity

    def update_playground(self):

        self.yielders_produce()
        self.check_timers()
        self.release_grasps()

        for zone in self.zones:
            zone.pre_step()




    def reset(self):
        # Reset the environment
        self.__init__(self.params)

    def generate_playground_image(self):
        # Update the screen of the environment
        self.topdown_view.fill(THECOLORS["black"])
        self.draw_visible_entities()
        self.draw_activation_radius()

        imgdata = pygame.surfarray.array3d(self.topdown_view)
        return imgdata

    def generate_playground_image_sensor(self):
        # Update the screen of the environment

        self.topdown_view.fill(THECOLORS["black"])
        self.draw_visible_entities()

        imgdata = pygame.surfarray.array3d(self.topdown_view)

        return imgdata

    def draw_visible_entities(self):

        for entity in self.physical_entities:

            if entity.visible:
                entity.draw(self.topdown_view)

        for agent in self.agents:
            agent.frame.draw(self.topdown_view)

    def draw_activation_radius(self):

        for entity in self.physical_entities:

            if entity.activable:

                entity.draw_activation_radius(self.topdown_view)
                entity.draw(self.topdown_view)

        for entity in self.zones:
            entity.draw(self.topdown_view)

    def yielders_produce(self):

        for yielder in self.yielders:

            if (random.random() < yielder.probability) and ( len(yielder.yielded_elements) < yielder.limit):
                new_obj_params = yielder.produce()
                new_obj = self.add_entity(new_obj_params, add_to_basics=False)
                yielder.yielded_elements.append(new_obj)

    def check_timers(self):

        for actionable in self.actionables:

            if actionable.actionable_type == 'door_opener' and actionable.door_opened:
                actionable.update_timer()

                if actionable.timer < 0 :
                    actionable.is_timing = False
                    self.space.add(actionable.door.pm_body, actionable.door.pm_shape)
                    actionable.door_opened = False


    def release_grasps(self):

        for agent in self.agents:

            if not agent.is_holding:

                for joint in agent.grasped:
                    self.space.remove(joint)
                agent.grasped = []

    def get_entity_from_shape(self, pm_shape):

        entity = [entity for entity in self.physical_entities if entity.pm_shape == pm_shape][0]
        return entity

    def get_agent_from_shape(self, pm_shape):

        for agent in self.agents:

            if agent.owns_shape(pm_shape):

                return agent

    def agent_absorbs(self, arbiter, space, data):

        agent_shape = arbiter.shapes[0]
        agent = self.get_agent_from_shape(agent_shape)

        absorbable_shape = arbiter.shapes[1]
        absorbable = self.get_entity_from_shape(absorbable_shape)

        reward = absorbable.reward
        agent.reward += reward

        self.space.remove(absorbable.pm_body, absorbable.pm_shape)
        self.physical_entities.remove(absorbable)

        if absorbable in self.absorbables:
            self.absorbables.remove(absorbable)

        for yielder in self.yielders:
            if absorbable in yielder.yielded_elements:
                yielder.yielded_elements.remove(absorbable)

        for dispenser in [actionable for actionable in self.actionables if actionable.actionable_type == 'dispenser']:
            if absorbable in dispenser.produced_elements:
                dispenser.produced_elements.remove(absorbable)

        return True


    def agent_activates(self, arbiter, space, data):

        agent_shape = arbiter.shapes[0]
        agent = self.get_agent_from_shape(agent_shape)

        activable_shape = arbiter.shapes[1]

        activable = [activable for activable in self.actionables if activable.pm_sensor == activable_shape][0]

        if agent.is_activating:

            agent.is_activating = False

            if activable.actionable_type == 'dispenser':

                if len(activable.produced_elements) < activable.limit:
                    new_entity_params = activable.actionate()
                    new_entity = self.add_entity(new_entity_params)
                    activable.produced_elements.append(new_entity)

            elif activable.actionable_type == 'door_opener':

                if not activable.door_opened:
                    activable.door_opened = True

                    door = activable.door

                    space.remove(door.pm_body, door.pm_shape)
                    door.visible = False

                    activable.start_timer()

            else:
                activable.actionate()

        return True

    def agent_grasps(self, arbiter, space, data):

        agent_shape = arbiter.shapes[0]
        agent = self.get_agent_from_shape(agent_shape)

        activable_shape = arbiter.shapes[1]
        activable = [activable for activable in self.actionables if activable.pm_sensor == activable_shape][0]

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
        agent = self.get_agent_from_shape(agent_shape)

        sensor_shape = arbiter.shapes[1]
        edible = [edible for edible in self.actionables if edible.pm_sensor == sensor_shape][0]

        if agent.is_eating:

            agent.is_eating = False

            space.remove(edible.pm_body, edible.pm_shape, edible.pm_sensor)
            space.add_post_step_callback(self.eaten_shrinks, edible, agent )

        return True

    def agent_enters_zone(self, arbiter, space, data):

        agent_shape = arbiter.shapes[0]
        agent = self.get_agent_from_shape(agent_shape)

        sensor_shape = arbiter.shapes[1]
        zone_reached = [zone for zone in self.zones if zone.pm_sensor == sensor_shape][0]

        if zone_reached.zone_type == 'end_zone':
            self.has_reached_termination = True
            reward = zone_reached.get_reward()
            agent.reward += reward

        elif zone_reached.zone_type == 'reward_zone':
            reward = zone_reached.get_reward()
            agent.reward += reward

        else:
            pass

        # agent.reward += termination_reward
        # agent.health += termination reward

        return True


    def eaten_shrinks(self, space, edible, agent):

        edible.actionate()

        agent.reward += edible.reward

        if edible.radius > 5 :

            space.add(edible.pm_body, edible.pm_shape, edible.pm_sensor)


        else:
            self.physical_entities.remove(edible)
            self.actionables.remove(edible)

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

        h_zone = self.space.add_collision_handler(collision_types['agent'], collision_types['zone'])
        h_zone.pre_solve = self.agent_enters_zone
