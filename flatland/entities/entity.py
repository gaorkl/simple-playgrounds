import pymunk
import pygame
import math
import numpy, cv2

import os
import yaml

from flatland.utils.position_utils import PositionAreaSampler, Trajectory
from flatland.utils.texture import Texture
from flatland.utils.config import geometric_shapes, CollisionTypes

#TODO: masks and physical shapes don't have the correct size sometimes (one pixel overlap)

class Entity:

    visible = True
    interactive = False

    absorbable = False
    edible = False

    movable = False
    follows_waypoints = False
    graspable = False

    index_entity = 0
    entity_type = None

    def __init__(self, initial_position=None, **entity_params):
        """ Base class for entities.

        Args:
            initial_position: Can be list, tuple (x,y,theta), Trajectory or PositionAreaSampler instances
            **entity_params: Additional Keyword Arguments

        Notes:
            For default configurations, see entity configs

        Keyword Args:
            graspable (:obj:'bool'): True if the object can be grasped by an agent.
                Default: False
            movable (:obj:'bool'): True if the object can be moved
                Default: False
            interaction_range (:obj:'int'): Size of the interaction area.
            texture: dictionary of texture parameters. Refer to the class Texture
            is_temporary_entity (:obj:'bool'): if True, object doesn't re-appear after playground reset.
                Default: False
            physical_shape (str): shape of the entity. Can be 'circle', 'square', 'rectangle', 'pentagon', 'hexagon'
            width_length: tuple of width, length to be set for rectangle shapes
            radius (:obj: 'float'): radius for non-rectangle shapes
            mass (:obj: 'float'): mass of the entity
        """

        # Internal counter to assign identity number and name to each entity
        self.name = self.entity_type + '_' + str(Entity.index_entity)
        Entity.index_entity += 1


        self.graspable = entity_params.get('graspable', self.graspable)
        self.movable = entity_params.get('movable', self.movable)

        if self.graspable:
            self.interactive = True
            self.movable = True

        self.interaction_range = entity_params.get('interaction_range', 5)

        self.physical_shape, self.mass, visible_size, interaction_size = self.get_physical_properties(entity_params)

        self.length, self.width, self.radius = visible_size
        self.interaction_length, self.interaction_width, self.interaction_radius = interaction_size

        # self.visible_vertices = self.compute_vertices(self.radius)
        # self.interaction_vertices = self.compute_vertices(self.interaction_radius)

        # To be set when entity is added to playground. Used to calculate correct coordinates
        self.size_playground = [0, 0]

        self.pm_body = self.create_pm_body()
        self.pm_elements = [self.pm_body]

        self.texture_params = entity_params['texture']
        self.texture_surface, self.texture_surface_interactive = self.create_texture(self.texture_params)

        self.pm_interaction_shape = None
        self.pm_visible_shape = None

        if self.visible:
            self.pm_visible_shape = self.create_pm_visible_shape()
            self.visible_mask = self.create_visible_mask()
            self.pm_elements.append(self.pm_visible_shape)

        if self.interactive:
            self.pm_interaction_shape = self.create_pm_interaction_shape()
            self.interaction_mask = self.create_interaction_mask()
            self.pm_elements.append(self.pm_interaction_shape)

        self.initial_position = initial_position



        # To remove temporary entities when reset
        self.is_temporary_entity = entity_params.get('is_temporary_entity', False)

        # Used to check if mask should be computed again
        self.prev_angle = None

    @staticmethod
    def parse_configuration(entity_type, key):

        if key is None:
            return {}

        fname = 'configs/' + entity_type + '_default.yml'

        __location__ = os.path.realpath(os.path.join(os.getcwd(), os.path.dirname(__file__)))
        with open(os.path.join(__location__, fname), 'r') as yaml_file:
            default_config = yaml.load(yaml_file)

        return default_config[key]

    def get_physical_properties(self, params):

        # Physical Shape
        physical_shape = params['physical_shape']

        # Properties of physical shape
        if physical_shape == 'rectangle':
            width, length = params['width_length']
            radius = math.sqrt(width**2 + length**2)/2
        else:
            radius = params['radius']
            length, width = math.sqrt(2) * radius, math.sqrt(2) * radius

        # properties of interaction shape. If not visible, take dimension of physical shape
        if physical_shape == 'rectangle':
            width_interaction = width + self.interaction_range * self.visible
            length_interaction = length + self.interaction_range * self.visible
            radius_interaction = math.sqrt(width_interaction**2 + length_interaction**2)

        else:
            radius_interaction = radius + self.interaction_range * self.visible
            width_interaction, length_interaction = math.sqrt(2) * radius_interaction, math.sqrt(2) * radius_interaction

        mass = params.get('mass', None)

        return physical_shape, mass, (width, length, radius), \
            (width_interaction, length_interaction, radius_interaction)

    def create_texture(self, texture_params):

        texture = Texture.create(texture_params)
        texture_surface = texture.generate(2*int(self.radius), 2*int(self.radius))

        texture_surface_interactive = pygame.transform.scale(texture_surface, (2*int(self.interaction_radius),
                                                                               2*int(self.interaction_radius)))

        return texture_surface, texture_surface_interactive

    @property
    def texture_params(self):
        return self._texture_params

    @texture_params.setter
    def texture_params(self, params):

        if isinstance(params, list):
            self._texture_params = {
                'texture_type': 'color',
                'color': params
            }
        else:
            self._texture_params = params

        self._texture_params['radius'] = self.radius
        self._texture_params['physical_shape'] = self.physical_shape

    @property
    def initial_position(self):

        # differentiate between case where initial position is fixed and case where it is random
        if isinstance(self._initial_position, (list, tuple)):
            return self._initial_position

        elif isinstance(self._initial_position, PositionAreaSampler):
            return self._initial_position.sample()

    @initial_position.setter
    def initial_position(self, init_pos):

        if isinstance(init_pos, Trajectory):
            self.trajectory = init_pos
            self._initial_position = next(self.trajectory)
            self.follows_waypoints = True

        elif isinstance(init_pos, (list, tuple, PositionAreaSampler)):
            self._initial_position = init_pos
            self.follows_waypoints = False

        else:
            raise ValueError('Initial position not valid')

    @property
    def position(self):

        x, y = self.pm_body.position
        phi = self.pm_body.angle

        coord_x = self.size_playground[0] - y
        coord_y = x
        coord_phi = (phi + math.pi / 2) % (2 * math.pi)

        return coord_x, coord_y, coord_phi

    @position.setter
    def position(self, pos):

        coord_x, coord_y, coord_phi = pos

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
    def velocity(self, vel):
        vx, vy, vphi = vel

        self.pm_body.velocity = (vx, vy)
        self.pm_body.angular_velocity = vphi

    def create_pm_body(self):

        if self.movable:
            inertia = self.compute_moments()
            pm_body = pymunk.Body(self.mass, inertia)

        else:
            pm_body = pymunk.Body(body_type=pymunk.Body.STATIC)

        return pm_body

    def compute_moments(self):

        vertices = self.compute_body_vertices(self.radius)

        if self.physical_shape == 'circle':
            moment = pymunk.moment_for_circle(self.mass, 0, self.radius)

        elif self.physical_shape in ['triangle', 'square', 'pentagon', 'hexagon']:
            moment = pymunk.moment_for_poly(self.mass, vertices)

        elif self.physical_shape == 'rectangle':
            moment = pymunk.moment_for_box(self.mass, (self.width, self.length))

        else:
            raise ValueError('Not implemented')

        return moment

    def compute_body_vertices(self, radius):

        if self.physical_shape in ['rectangle', 'circle']:
            return None

        else:
            number_sides = geometric_shapes[self.physical_shape]

            vertices = []
            for n in range(number_sides):
                vertices.append([radius*math.cos(n * 2*math.pi / number_sides),
                                 radius * math.sin(n * 2*math.pi / number_sides)])

            return vertices

    def create_pm_visible_shape(self):

        vertices = self.compute_visible_vertices()

        if self.physical_shape == 'circle':
            pm_visible_shape = pymunk.Circle(self.pm_body, self.radius)

        elif self.physical_shape in ['triangle', 'square', 'pentagon', 'hexagon']:
            pm_visible_shape = pymunk.Poly(self.pm_body, vertices)

        elif self.physical_shape == 'rectangle':
            pm_visible_shape = pymunk.Poly.create_box(self.pm_body, (self.width, self.length))

        else:
            raise ValueError

        pm_visible_shape.friction = 0.8
        pm_visible_shape.elasticity = 0.5

        return pm_visible_shape

    def compute_visible_vertices(self):

        vertices = []

        if self.physical_shape == 'rectangle':

            w, l = self.width -1 , self.length - 1

            coord_pts_in_entity_base = [[w/2., l/2.], [-w/2., l/2.], [-w/2., -l/2.], [w/2., -l/2.]]


            for coord in coord_pts_in_entity_base:

                x = coord[0] * math.cos(self.pm_body.angle) - coord[1] * math.sin(self.pm_body.angle)
                y = coord[0] * math.sin(self.pm_body.angle) + coord[1] * math.cos(self.pm_body.angle)

                vertices.append([ x, y])
        else:
            radius = self.radius
            number_sides = geometric_shapes[self.physical_shape]

            for n in range(number_sides):
                vertices.append([ radius*math.cos( n * 2*math.pi / number_sides + self.pm_body.angle ),
                                  radius * math.sin(n * 2*math.pi / number_sides + self.pm_body.angle )])

        return vertices


    def create_visible_mask(self):

        alpha = 255

        if self.physical_shape == 'circle':

            mask = pygame.Surface(( int(2*self.radius  ) , int(2*self.radius  )), pygame.SRCALPHA)
            mask.fill((0, 0, 0, 0))
            pygame.draw.circle(mask, (255, 255, 255, alpha), (int(self.radius), int(self.radius)), int(self.radius) )

        else:

            vert = self.compute_visible_vertices()
            vertices = [[x[1] + self.radius  , x[0] + self.radius  ] for x in vert]

            mask = pygame.Surface((2 * self.radius , 2 * self.radius ), pygame.SRCALPHA)
            mask.fill((0, 0, 0, 0))
            pygame.draw.polygon(mask, (255, 255, 255, alpha), vertices)



        # Apply texture on mask

        # if self.physical_shape == 'square':
        texture_visible_surface = pygame.transform.rotate(self.texture_surface, 180*self.pm_body.angle/math.pi)
        delta = ( (2 * self.radius + 1) - texture_visible_surface.get_width() , (2 * self.radius + 1) - texture_visible_surface.get_height())

        delta = (delta[0]/2, delta[1]/2)
        # delta = (0,0)

        mask.blit(texture_visible_surface, delta, None, pygame.BLEND_MULT)

        # img_sensor = pygame.surfarray.array3d(mask)
        # img_sensor = numpy.rot90(img_sensor, 1, (1, 0))
        # img_sensor = img_sensor[::-1, :, ::-1]
        #
        # if self.physical_shape == 'rectangle':
        #     # print(self.name, vert)
        #     cv2.imshow('mask '+str(self.radius), img_sensor)


        return mask


    def create_pm_interaction_shape(self):

        vertices = self.compute_interaction_vertices()

        if self.physical_shape == 'circle':
            pm_interaction_shape = pymunk.Circle(self.pm_body, self.interaction_radius)

        elif self.physical_shape in ['triangle', 'square', 'pentagon', 'hexagon']:
            pm_interaction_shape = pymunk.Poly(self.pm_body, vertices)

        elif self.physical_shape == 'rectangle':
            pm_interaction_shape = pymunk.Poly.create_box(self.pm_body,
                                                          (self.interaction_width, self.interaction_length))

        else:
            raise ValueError

        pm_interaction_shape.sensor = True
        pm_interaction_shape.collision_type = CollisionTypes.INTERACTIVE

        return pm_interaction_shape




    def create_interaction_mask(self):

        alpha = 75

        if self.physical_shape == 'circle':

            mask = pygame.Surface(( int(2*self.interaction_radius ) , int(2*self.interaction_radius )), pygame.SRCALPHA)
            mask.fill((0, 0, 0, 0))
            pygame.draw.circle(mask, (255, 255, 255, alpha), (int(self.interaction_radius), int(self.interaction_radius)), int(self.interaction_radius))

        else:

            vert = self.compute_interaction_vertices()
            vertices = [[x[1] + self.interaction_radius , x[0] + self.interaction_radius ] for x in vert]

            mask = pygame.Surface((2 * self.interaction_radius  , 2 * self.interaction_radius  ), pygame.SRCALPHA)
            mask.fill((0, 0, 0, 0))
            pygame.draw.polygon(mask, (255, 255, 255, alpha), vertices)



        # Apply texture on mask

        # if self.physical_shape == 'square':
        texture_interaction_surface = pygame.transform.rotate(self.texture_surface_interactive, 180*self.pm_body.angle/math.pi)
        delta = ( (2 * self.interaction_radius + 1) - texture_interaction_surface.get_width() ,
                  (2 * self.interaction_radius + 1) - texture_interaction_surface.get_height())

        delta = (delta[0]/2, delta[1]/2)
        mask.blit(texture_interaction_surface, delta, None, pygame.BLEND_MULT)

        return mask





    def compute_interaction_vertices(self):

        vertices = []

        if self.physical_shape == 'rectangle':

            w, l = self.interaction_width - 1, self.interaction_length - 1

            coord_pts_in_entity_base = [[w / 2., l / 2.], [-w / 2., l / 2.], [-w / 2., -l / 2.], [w / 2., -l / 2.]]

            for coord in coord_pts_in_entity_base:
                x = coord[0] * math.cos(self.pm_body.angle) - coord[1] * math.sin(self.pm_body.angle)
                y = coord[0] * math.sin(self.pm_body.angle) + coord[1] * math.cos(self.pm_body.angle)

                vertices.append([x, y])
        else:
            radius = self.interaction_radius - 1
            number_sides = geometric_shapes[self.physical_shape]

            for n in range(number_sides):
                vertices.append([radius * math.cos(n * 2 * math.pi / number_sides + self.pm_body.angle),
                                 radius * math.sin(n * 2 * math.pi / number_sides + self.pm_body.angle)])

        return vertices



    def draw(self, surface, draw_interaction=False, force_recompute_mask = False):
        """
        Draw the obstacle on the environment screen
        """

        if self.prev_angle != self.position[2] or force_recompute_mask:
            self.visible_mask = self.create_visible_mask()

            if self.interactive:
                self.interaction_mask = self.create_interaction_mask()

            self.prev_angle = self.position[2]


        if draw_interaction and self.interactive:

            mask_rect = self.interaction_mask.get_rect()
            mask_rect.center = self.pm_body.position[1], self.pm_body.position[0]
            surface.blit(self.interaction_mask, mask_rect, None)

        if self.visible:

            mask_rect = self.visible_mask.get_rect()
            mask_rect.center = self.pm_body.position[1], self.pm_body.position[0]
            surface.blit(self.visible_mask, mask_rect, None)
    #
    # def get_mask(self):


    def update(self):

        if self.follows_waypoints:
            self.position = next(self.trajectory)

    def pre_step(self):
        pass

    def reset(self):

        if self.follows_waypoints:
            self.trajectory.reset()

        self.velocity = [0, 0, 0]
        self.position = self.initial_position

#
# class EntityGenerator:
#
#     subclasses = {}
#
#     @classmethod
#     def register(cls, entity_type):
#         def decorator(subclass):
#             cls.subclasses[entity_type] = subclass
#             return subclass
#
#         return decorator
#
#     @classmethod
#     def create(cls, entity_type, **kwargs):
#
#         if entity_type not in cls.subclasses:
#             raise ValueError('Entity type not implemented:' + entity_type)
#
#         return cls.subclasses[entity_type](**kwargs)
