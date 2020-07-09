from ..entities.entity import *
from ..utils.position_utils import *
from ..utils.config import *


class PlaygroundGenerator:

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


class Playground:

    scene_entities = []

    def __init__(self, size, **scene_params):

        # Generate Scene
        self.scene_size = size
        self.width, self.length = self.scene_size

        # Initialization of the pymunk space, this space is responsible for modelling all the physics
        self.space = None
        self.initialize_space()

        # Data structures to save list of entities, and relations between them
        self.physical_entities = []

        self.entities = []
        self.fields = []
        self.disappeared = []
        self.grasped = {}

        # Add entities declared in the scene
        for scene_entity in self.scene_entities:
            self.add_entity(scene_entity)

        self.handle_collisions()

        self.agents = []

        self.has_reached_termination = False

        self.agent_starting_area = None

    @staticmethod
    def parse_configuration(entity_type, key):

        if key is None:
            return {}

        fname = 'configs/' + entity_type + '_default.yml'

        __location__ = os.path.realpath(os.path.join(os.getcwd(), os.path.dirname(__file__)))
        with open(os.path.join(__location__, fname), 'r') as yaml_file:
            default_config = yaml.load(yaml_file)

        return default_config[key]

    def initialize_space(self):

        self.space = pymunk.Space()
        self.space.gravity = pymunk.Vec2d(0., 0.)
        self.space.damping = SPACE_DAMPING

    def add_agent(self, agent):

        self.agents.append(agent)

        agent.size_playground = [self.width, self.length]

        if agent.initial_position is not None:
            pass

        elif self.agent_starting_area is not None:
            agent.initial_position = self.agent_starting_area

        else:
            agent.initial_position = [self.width / 2, self.length / 2, 0]

        agent.position = agent.initial_position

        for body_part in agent.body_parts:
            self.space.add(*body_part.pm_elements)

    def remove_agents(self):

        for agent in self.agents:
            for part in agent.body_parts:
                self.space.remove(*part.pm_elements)
                part.velocity = [0, 0, 0]
        self.agents = []

    def add_entity(self, new_entity, new_position = True):

        new_entity.size_playground = [self.width, self.length]

        if new_entity.entity_type is 'field':
            self.fields.append(new_entity)

        else:
            if new_position:
                new_entity.position = new_entity.initial_position

            self.space.add(*new_entity.pm_elements)
            self.entities.append(new_entity)
            if new_entity in self.disappeared:
                self.disappeared.remove(new_entity)

    def remove_entity(self, disappearing_entity):

        self.space.remove(*disappearing_entity.pm_elements)
        self.entities.remove(disappearing_entity)

        if not disappearing_entity.is_temporary_entity:
            self.disappeared.append(disappearing_entity)

        for entity in self.entities:
            if entity.entity_type is 'dispenser' and disappearing_entity in entity.produced_entities:
                entity.produced_entities.remove(disappearing_entity)

        for entity in self.fields:
            if disappearing_entity in entity.produced_entities:
                entity.produced_entities.remove(disappearing_entity)

        if disappearing_entity in self.grasped.keys():
            body_part = self.grasped[disappearing_entity]
            self.space.remove( *body_part.grasped )
            body_part.grasped = []

    def update_playground(self):

        for entity in self.entities:
            entity.update()
            entity.pre_step()

            if entity.follows_waypoints:
                self.space.reindex_shapes_for_body(entity.pm_body)

        self.fields_produce()
        self.check_timers()
        self.release_grasps()

    def reset(self):

        print('reset playground')

        # remove entities and filter out entities which are temporary
        for entity in self.entities.copy():
            self.remove_entity(entity)

        # reset and replace entities that are not temporary
        for entity in self.disappeared.copy():
            entity.reset()
            self.add_entity(entity)

        for entity in self.fields:
            entity.reset()

        self.has_reached_termination = False

    def fields_produce(self):

        for field in self.fields:

            if field.can_produce():
                new_entity = field.produce()
                self.add_entity(new_entity)

    def check_timers(self):

        for entity in self.entities:

            if entity.entity_type == 'switch' and hasattr(entity, 'timer'):

                if entity.door.opened and entity.timer == 0:
                    self.add_entity(entity.door)
                    entity.door.close_door()
                    entity.reset_timer()

    def release_grasps(self):

        for agent in self.agents:

            for part in agent.body_parts:
                if not part.is_holding and part.can_grasp:

                    for joint in part.grasped:
                        self.space.remove(joint)
                    part.grasped = []

    def get_entity_from_shape(self, pm_shape):

        entity = next(iter([ent for ent in self.entities if pm_shape in ent.pm_elements]), None)
        return entity

    def get_agent_from_shape(self, pm_shape):
        for agent in self.agents:
            if agent.owns_shape(pm_shape):
                return agent

    def get_closest_agent(self, ent):

        dist_list = [(a.position[0] - ent.position[0])**2 + (a.position[1] - ent.position[1])**2 for a in self.agents]
        index_min_dist = dist_list.index(min(dist_list))
        closest_agent = self.agents[index_min_dist]

        return closest_agent

    def agent_touches_entity(self, arbiter, space, data):

        agent = self.get_agent_from_shape(arbiter.shapes[0])
        touched_entity = self.get_entity_from_shape(arbiter.shapes[1])

        agent.reward += touched_entity.reward

        list_remove, list_add = touched_entity.activate()

        for entity_removed in list_remove:
            self.remove_entity(entity_removed)

        for entity_added in list_add:
            self.add_entity(entity_added)

        if touched_entity.terminate_upon_contact:
            self.has_reached_termination = True

        return True


    def agent_interacts(self, arbiter, space, data):

        agent = self.get_agent_from_shape(arbiter.shapes[0])
        body_part = agent.get_bodypart_from_shape(arbiter.shapes[0])
        interacting_entity = self.get_entity_from_shape(arbiter.shapes[1])

        if body_part.is_activating: # and (interacting_entity.entity_type is 'dispenser'):

            agent.reward += interacting_entity.reward

            list_remove, list_add = interacting_entity.activate(None)

            for entity_removed in list_remove:
                self.remove_entity(entity_removed)

            for entity_added in list_add:
                self.add_entity(entity_added)

            if interacting_entity.terminate_upon_contact:
                self.has_reached_termination = True

            body_part.is_activating = False

        return True

    def agent_grasps(self, arbiter, space, data):

        agent = self.get_agent_from_shape(arbiter.shapes[0])
        body_part = agent.get_bodypart_from_shape(arbiter.shapes[0])
        interacting_entity = self.get_entity_from_shape(arbiter.shapes[1])

        if body_part.is_grasping and not body_part.is_holding  :

            body_part.is_holding = True

            j1 = pymunk.PinJoint(interacting_entity.pm_body, body_part.pm_body, (0,5), (0,-5))
            j2 = pymunk.PinJoint(interacting_entity.pm_body, body_part.pm_body, (0,-5), (0,5))
            j3 = pymunk.PinJoint(interacting_entity.pm_body, body_part.pm_body, (5,5), (0,5))
            j4 = pymunk.PinJoint(interacting_entity.pm_body, body_part.pm_body, (5,-5), (0,5))

            self.space.add(j1, j2, j3, j4)
            body_part.grasped = [j1, j2, j3, j4]

            self.grasped[interacting_entity] = body_part

        return True

    def agent_enters_zone(self, arbiter, space, data):

        agent = self.get_agent_from_shape(arbiter.shapes[0])
        zone_reached = self.get_entity_from_shape(arbiter.shapes[1])

        agent.reward += zone_reached.reward

        if zone_reached.terminate_upon_contact:
            self.has_reached_termination = True

        return True

    def gem_interacts(self, arbiter, space, data):

        gem = self.get_entity_from_shape(arbiter.shapes[0])
        interacting_entity = self.get_entity_from_shape(arbiter.shapes[1])

        agent = self.get_closest_agent(gem)
        agent.reward += interacting_entity.reward

        list_remove, list_add = interacting_entity.activate(gem)

        for entity_removed in list_remove:
            self.remove_entity(entity_removed)

        for entity_added in list_add:
            self.add_entity(entity_added)

        if interacting_entity.terminate_upon_contact:
            self.has_reached_termination = True

        return True

    def agent_eats(self, arbiter, space, data):

        agent = self.get_agent_from_shape(arbiter.shapes[0])
        body_part = agent.get_bodypart_from_shape(arbiter.shapes[0])
        edible_entity = self.get_entity_from_shape(arbiter.shapes[1])

        if body_part.is_eating :

            agent.reward += edible_entity.get_reward()

            self.remove_entity(edible_entity)
            completely_eaten = edible_entity.eats()

            if not completely_eaten:
                self.add_entity(edible_entity, new_position=False)

            body_part.is_eating = False

        return True

    def handle_collisions(self):

        # TODO: replace all collisoin handlers with:
        # - agent agent
        # - agent interactive
        # - interactive interactive

        # Collision handlers
        h_touch = self.space.add_collision_handler(CollisionTypes.AGENT, CollisionTypes.CONTACT)
        h_touch.pre_solve = self.agent_touches_entity

        h_eat = self.space.add_collision_handler(CollisionTypes.AGENT, CollisionTypes.EDIBLE)
        h_eat.pre_solve = self.agent_eats

        h_interact = self.space.add_collision_handler(CollisionTypes.AGENT, CollisionTypes.INTERACTIVE)
        h_interact.pre_solve = self.agent_interacts

        h_zone = self.space.add_collision_handler(CollisionTypes.AGENT, CollisionTypes.PASSIVE)
        h_zone.pre_solve = self.agent_enters_zone

        h_gem_interactive = self.space.add_collision_handler(CollisionTypes.GEM, CollisionTypes.INTERACTIVE)
        h_gem_interactive.pre_solve = self.gem_interacts

        h_grasp = self.space.add_collision_handler(CollisionTypes.AGENT, CollisionTypes.GRASPABLE)
        h_grasp.pre_solve = self.agent_grasps
