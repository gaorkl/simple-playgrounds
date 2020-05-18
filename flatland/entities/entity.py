import pymunk, math, pygame
from flatland.utils.config import *
from flatland.utils.position_utils import *
from flatland.utils import texture
import os, yaml

from copy import deepcopy


class Entity():

    visible = True
    interactive = False

    absorbable = False
    activable = False
    edible = False

    movable = False
    follows_waypoints = False
    graspable = False

    index_entity = 0
    entity_type = None

    def __init__(self, **entity_params):
        """
        Instantiate an obstacle with the following parameters
        :param pos: 2d tuple or 'random', position of the fruit
        :param environment: the environment calling the creation of the fruit
        """

        self.parse_parameters(entity_params)

        if self.graspable:
            self.interactive = True
            self.movable = True

        self.pm_body = None
        self.pm_interaction_shape = None
        self.pm_visible_shape = None

        self.create_pm_body()
        self.pm_elements =[self.pm_body]

        self.create_texture()

        if self.visible:
            self.create_pm_visible_shape()
            self.create_visible_mask()
            self.pm_elements.append(self.pm_visible_shape)

        if self.interactive:
            self.create_pm_interaction_shape()
            self.create_interaction_mask()
            self.pm_elements.append(self.pm_interaction_shape)

        # if self.trajectory_params is not None:
        #     self.follows_waypoints = True
        #     self.generate_trajectory()
        #     self.initial_position = self.trajectory_points[0]

        initial_position = entity_params.get('initial_position')
        if isinstance(initial_position, Trajectory):
            self.trajectory = initial_position
            self.initial_position = next(self.trajectory)
            self.follows_waypoints = True

        elif isinstance(initial_position, (list, tuple)):
            self.initial_position = initial_position
        else:
            raise ValueError('Initial position not set')

        # Internal counter to assign identity number to each entity
        self.name = self.entity_type+'_' + str(Entity.index_entity)
        Entity.index_entity += 1

        # To be set when entity is added to playground
        self.size_playground = None


    def parse_parameters(self, params):

        # Optional parameters
        self.graspable = params.get('graspable', self.graspable)
        self.movable = params.get('movable', self.movable)
        self.is_temporary_entity = params.get('is_temporary_entity', False)

        self.mass = params.get('mass', None)

        # Physical Shape
        self.physical_shape = params['physical_shape']

        if self.physical_shape == 'rectangle':
            self.length, self.width = params['width_length']
            self.radius = max(self.width, self.length)
        elif self.physical_shape == 'circle':
            self.radius = params['radius']
        else:
            self.radius = params['radius']
            self.visible_vertices = self.compute_vertices(self.radius)

        # Interaction shape. If not visible, take dimension of physical shape
        self.interaction_range = params.get('interaction_range', 5)

        if self.physical_shape == 'rectangle':
            self.width_interaction = self.width + self.interaction_range * self.visible
            self.length_interaction = self.length + self.interaction_range * self.visible
            self.radius_interaction = max(self.width_interaction, self.length_interaction)

        else:
            self.radius_interaction = self.radius + self.interaction_range * self.visible

        self.texture_params = params['texture']
        self.texture_params['radius'] = self.radius





    def create_texture(self):

        self.texture = texture.Texture.create(self.texture_params)
        self.texture_surface = self.texture.generate(2*int(self.radius), 2*int(self.radius))


    def create_pm_body(self):

        if self.movable:
            inertia = self.compute_moments()
            self.pm_body = pymunk.Body(self.mass, inertia)

        else:
            self.pm_body = pymunk.Body(body_type=pymunk.Body.STATIC)


    def parse_configuration(self, entity_type, key):

        if key is None:
            return {}

        fname = 'configs/' + entity_type + '_default.yml'

        __location__ = os.path.realpath(os.path.join(os.getcwd(), os.path.dirname(__file__)))
        with open(os.path.join(__location__, fname), 'r') as yaml_file:
            default_config = yaml.load(yaml_file)

        return default_config[key]


    @property
    def texture_params(self):
        return self._texture_params

    @texture_params.setter
    def texture_params(self, params):

        if isinstance(params, list):
            self._texture_params =   {
                'texture_type' : 'color',
                'color' : params
            }
        else:
            self._texture_params = params

        self._texture_params['radius'] = self.radius
        self._texture_params['physical_shape'] = self.physical_shape


    @property
    def initial_position(self):

        # differentiate between case where initial position is fixed and case where it is random

        if isinstance( self._initial_position, list ) or isinstance( self._initial_position, tuple ) :
            return self._initial_position

        else:
            return self._initial_position.sample()

    @initial_position.setter
    def initial_position(self, position):

        self._initial_position = position


    @property
    def position(self):

        x, y = self.pm_body.position
        phi = self.pm_body.angle

        coord_x = self.size_playground[0] - y
        coord_y = x
        coord_phi = (phi + math.pi / 2) % (2 * math.pi)

        return coord_x, coord_y, coord_phi

    @position.setter
    def position(self, position):

        coord_x, coord_y, coord_phi = position

        # make sure that coordinates are within playground
        coord_x = max(min(self.size_playground[0], coord_x), 0)
        coord_y = max(min(self.size_playground[1], coord_y), 0)

        y = self.size_playground[0] - coord_x
        x = coord_y
        phi = coord_phi - math.pi / 2

        if self.physical_shape not in ['rectangle', 'circle']:
            phi = phi + math.pi / geometric_shapes[self.physical_shape]

        self.pm_body.position = x, y
        self.pm_body.angle = phi

    @property
    def velocity(self):
        vx, vy = self.pm_body.velocity
        vphi = self.pm_body.angular_velocity

        vx, vy = -vy, vx
        return vx, vy, vphi

    @velocity.setter
    def velocity(self, velocity):
        vx, vy, vphi = velocity

        self.pm_body.velocity = (vx, vy)
        self.pm_body.angular_velocity = vphi


    def create_pm_visible_shape(self):

        if self.physical_shape == 'circle':

            self.pm_visible_shape = pymunk.Circle(self.pm_body, self.radius)

        elif self.physical_shape in ['triangle', 'square', 'pentagon', 'hexagon']:

            self.pm_visible_shape = pymunk.Poly(self.pm_body, self.visible_vertices)

        elif self.physical_shape == 'rectangle':

            self.pm_visible_shape = pymunk.Poly.create_box(self.pm_body, (self.width, self.length))

        else:
            raise ValueError

        self.pm_visible_shape.friction = 1.
        self.pm_visible_shape.elasticity = 0.95


    def create_pm_interaction_shape(self):

        if self.physical_shape in ['triangle', 'square', 'pentagon', 'hexagon'] :
            self.interaction_vertices = self.compute_vertices(self.radius_interaction)


        if self.physical_shape == 'circle':

            self.pm_interaction_shape = pymunk.Circle(self.pm_body, self.radius_interaction)

        elif self.physical_shape in ['triangle', 'square', 'pentagon', 'hexagon']:

            self.pm_interaction_shape = pymunk.Poly(self.pm_body, self.interaction_vertices)

        elif self.physical_shape == 'rectangle':

            self.pm_interaction_shape = pymunk.Poly.create_box(self.pm_body, (self.width_interaction, self.length_interaction))

        else:
            raise ValueError

        self.pm_interaction_shape.sensor = True
        self.pm_interaction_shape.collision_type = collision_types['interactive']


    def create_visible_mask(self):

        alpha = 255

        if self.physical_shape == 'rectangle':

            texture_visible_surface = pygame.transform.scale(self.texture_surface, (2*int(self.radius),2*int(self.radius)))
            mask = pygame.Surface((int(self.length), int(self.width)), pygame.SRCALPHA)
            mask.fill((0, 0, 0, 0))
            pygame.draw.rect(mask, (255, 255, 255, alpha), ((0, 0), (int(self.length), int(self.width))))

        elif self.physical_shape == 'circle':

            texture_visible_surface = pygame.transform.scale(self.texture_surface, (2*int(self.radius),2*int(self.radius)))
            mask = pygame.Surface((int(self.radius) * 2, int(self.radius) * 2), pygame.SRCALPHA)
            mask.fill((0, 0, 0, 0))
            pygame.draw.circle(mask, (255, 255, 255, alpha), (int(self.radius), int(self.radius)), int(self.radius))

        else:

            bb = self.pm_visible_shape.cache_bb()

            length = int(bb.top - bb.bottom)
            width = int(bb.right - bb.left)

            vertices = [[x[1] + length, x[0] + width] for x in self.visible_vertices]

            texture_visible_surface = pygame.transform.scale(self.texture_surface,((2 * length, 2 * width)) )
            mask = pygame.Surface((2 * length, 2 * width), pygame.SRCALPHA)
            mask.fill((0, 0, 0, 0))
            pygame.draw.polygon(mask, (255, 255, 255, alpha), vertices)

        # Apply texture on mask
        mask.blit(texture_visible_surface, (0, 0), None, pygame.BLEND_MULT)
        self.visible_mask = mask


    def create_interaction_mask(self):


        alpha = 75

        if self.physical_shape == 'rectangle':

            width, length = int(self.width_interaction), int(self.length_interaction)

            texture_interactive_surface = pygame.transform.scale(self.texture_surface,(2*int(self.radius_interaction), 2*int(self.radius_interaction)))
            mask = pygame.Surface((length, width), pygame.SRCALPHA)
            mask.fill((0, 0, 0, 0))
            pygame.draw.rect(mask, (255, 255, 255, alpha), ((0, 0), (length, width)))

        elif self.physical_shape == 'circle':

            radius = int(self.radius_interaction)

            texture_interactive_surface = pygame.transform.scale(self.texture_surface,(2*int(self.radius_interaction), 2*int(self.radius_interaction)))

            mask = pygame.Surface((radius * 2, radius * 2), pygame.SRCALPHA)
            mask.fill((0, 0, 0, 0))
            pygame.draw.circle(mask, (255, 255, 255, alpha), (radius, radius), radius)

        else:

            bb = self.pm_interaction_shape.cache_bb()

            length = bb.top - bb.bottom
            width = bb.right - bb.left

            vertices = [[x[1] + length, x[0] + width] for x in self.interaction_vertices]

            texture_interactive_surface = pygame.transform.scale(self.texture_surface, ((int(2 * length), int(2 * width))))
            mask = pygame.Surface((2 * length, 2 * width), pygame.SRCALPHA)
            mask.fill((0, 0, 0, 0))
            pygame.draw.polygon(mask, (255, 255, 255, alpha), vertices)

        # Apply texture on mask
        mask.blit(texture_interactive_surface, (0, 0), None, pygame.BLEND_MULT)
        self.interaction_mask = mask



    def compute_vertices(self, radius):

        number_sides = geometric_shapes[self.physical_shape]

        vertices = []
        for n in range(number_sides):
            vertices.append( [ radius*math.cos(n * 2*math.pi / number_sides), radius* math.sin(n * 2*math.pi / number_sides) ])

        return vertices



    def compute_moments(self):

        if self.physical_shape == 'circle':

            moment = pymunk.moment_for_circle(self.mass, 0, self.radius)

        elif self.physical_shape in ['triangle', 'square', 'pentagon', 'hexagon']:

            moment = pymunk.moment_for_poly(self.mass, self.visible_vertices)

        elif self.physical_shape == 'rectangle':

            moment =  pymunk.moment_for_box(self.mass, (self.width, self.length))

        else:

            raise ValueError('Not implemented')

        return moment

    def draw(self, surface, draw_interaction = False):
        """
        Draw the obstacle on the environment screen
        """

        if draw_interaction and self.interactive:
            mask_rotated = pygame.transform.rotate(self.interaction_mask, self.pm_body.angle * 180 / math.pi)
            mask_rect = mask_rotated.get_rect()
            mask_rect.center = self.pm_body.position[1], self.pm_body.position[0]
            surface.blit(mask_rotated, mask_rect, None)

        if self.visible:
            mask_rotated = pygame.transform.rotate(self.visible_mask, self.pm_body.angle * 180 / math.pi)
            mask_rect = mask_rotated.get_rect()
            mask_rect.center = self.pm_body.position[1], self.pm_body.position[0]
            surface.blit(mask_rotated, mask_rect, None)

    def update(self):

        if self.follows_waypoints:

            self.position = next(self.trajectory)


    def pre_step(self):
        pass


    def reset(self):

        if self.trajectory is not None:
            self.trajectory.reset()

        self.velocity = [0, 0, 0]

        self.position = self.initial_position


class EntityGenerator():

    subclasses = {}

    @classmethod
    def register_subclass(cls, entity_type):
        def decorator(subclass):
            cls.subclasses[entity_type] = subclass
            return subclass

        return decorator

    @classmethod
    def create(cls, entity_type, entity_config):

        if entity_type is None:
            entity_type = entity_config.get('entity_type')

        if entity_type not in cls.subclasses:
            raise ValueError('Entity type not implemented:' + entity_type)

        return cls.subclasses[entity_type](entity_config)