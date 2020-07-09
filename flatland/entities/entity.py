import pymunk
import pygame
import math

import os
import yaml

from flatland.utils.position_utils import PositionAreaSampler, Trajectory
from flatland.entities.texture import TextureGenerator
from flatland.utils.definitions import geometric_shapes, CollisionTypes

# TODO: masks and physical shapes don't have the correct size sometimes (one pixel overlap)


class Entity:

    visible = True
    interactive = False

    absorbable = False
    edible = False

    movable = False
    follows_waypoints = False
    graspable = False

    terminate_upon_contact = False

    index_entity = 0
    entity_type = 'entity'

    def __init__(self, initial_position=None, **entity_params):
        """ Base class for entities.

        Args:
            initial_position: Can be list, tuple (x,y,theta), Trajectory or PositionAreaSampler instances
            **entity_params: Additional Keyword Arguments

        Notes:
            For default configurations, see entity configs

        Keyword Args:
            name (str): Name of the entity. If none is provided, name is generated automatically.
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
        self.name = entity_params.get('name', self.entity_type + '_' + str(Entity.index_entity))
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

        self.pm_body = self.create_pm_body()
        self.pm_elements = [self.pm_body]

        self.texture_surface = self.create_texture(entity_params['texture'])

        self.pm_interaction_shape = None
        self.pm_visible_shape = None

        if self.visible:
            self.pm_visible_shape = self.create_pm_shape()
            self.visible_mask = self.create_mask()
            self.pm_elements.append(self.pm_visible_shape)

        if self.interactive:
            self.pm_interaction_shape = self.create_pm_shape(is_interactive=True)
            self.interaction_mask = self.create_mask(is_interactive=True)
            self.pm_elements.append(self.pm_interaction_shape)

        if self.graspable:
            self.pm_grasp_shape = self.create_pm_shape(is_interactive=True)
            self.pm_grasp_shape.collision_type = CollisionTypes.GRASPABLE
            self.grasp_mask = self.create_mask(is_interactive=True)
            self.pm_elements.append(self.pm_grasp_shape)

        self.initial_position = initial_position

        # To remove temporary entities when reset
        self.is_temporary_entity = entity_params.get('is_temporary_entity', False)

        # Used to check if mask should be computed again
        self.prev_angle = self.pm_body.angle

        # To be set when entity is added to playground. Used to calculate correct coordinates
        self.size_playground = [0, 0]
        self.velocity = [0, 0, 0]
        self.position = [0, 0, 0]

    @staticmethod
    def _parse_configuration(entity_type, key):

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

        if isinstance(texture_params, list):
            texture_params = {
                'texture_type': 'color',
                'color': texture_params
            }

        texture_params['radius'] = self.radius
        texture_params['physical_shape'] = self.physical_shape

        texture = TextureGenerator.create(texture_params)
        texture_surface = texture.generate()

        return texture_surface

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

        if self.physical_shape == 'circle':
            moment = pymunk.moment_for_circle(self.mass, 0, self.radius)

        elif self.physical_shape in ['triangle', 'square', 'pentagon', 'hexagon']:
            vertices = self.compute_vertices(angle=0)
            moment = pymunk.moment_for_poly(self.mass, vertices)

        elif self.physical_shape == 'rectangle':
            moment = pymunk.moment_for_box(self.mass, (self.width, self.length))

        else:
            raise ValueError('Not implemented')

        return moment

    def compute_vertices(self, angle, is_interactive=False, border = 0):

        vertices = []

        if self.physical_shape == 'rectangle':

            if is_interactive:
                width = self.interaction_width
                length = self.interaction_length
            else:
                width = self.width + border
                length = self.length + border

            coord_pts_in_entity_base = [[width/2., length/2.], [-width/2., length/2.],
                                        [-width/2., -length/2.], [width/2., -length/2.]]

            for coord in coord_pts_in_entity_base:

                x = coord[0] * math.cos(angle) - coord[1] * math.sin(angle)
                y = coord[0] * math.sin(angle) + coord[1] * math.cos(angle)

                vertices.append([x, y])
        else:
            if is_interactive:
                radius = self.interaction_radius + border
            else:
                radius = self.radius + border

            number_sides = geometric_shapes[self.physical_shape]

            for n in range(number_sides):
                vertices.append([radius*math.cos(n * 2*math.pi / number_sides + angle),
                                radius * math.sin(n * 2*math.pi / number_sides + angle)])

        return vertices

    def create_pm_shape(self, is_interactive=False):

        if is_interactive:
            radius = self.interaction_radius
            width = self.interaction_width
            length = self.interaction_length
        else:
            radius = self.radius
            width = self.width
            length = self.length

        if self.physical_shape == 'circle':
            pm_shape = pymunk.Circle(self.pm_body, radius)

        elif self.physical_shape in ['triangle', 'square', 'pentagon', 'hexagon']:
            vertices = self.compute_vertices(angle=self.pm_body.angle, is_interactive=is_interactive)
            pm_shape = pymunk.Poly(self.pm_body, vertices)

        elif self.physical_shape == 'rectangle':
            pm_shape = pymunk.Poly.create_box(self.pm_body, (width, length))

        else:
            raise ValueError

        if is_interactive:
            pm_shape.sensor = True
        else:
            pm_shape.friction = 0.8
            pm_shape.elasticity = 0.5

        return pm_shape

    def create_mask(self, is_interactive=False):

        if is_interactive:
            radius = self.interaction_radius
            alpha = 75
        else:
            radius = self.radius
            alpha = 255

        if self.physical_shape == 'circle':

            mask = pygame.Surface((int(2*radius), int(2*radius)), pygame.SRCALPHA)
            mask.fill((0, 0, 0, 0))
            pygame.draw.circle(mask, (255, 255, 255, alpha), (int(radius), int(radius)), int(radius))

        else:

            vert = self.compute_vertices(angle=self.pm_body.angle, is_interactive=is_interactive, border = -1)
            vertices = [[x[1] + radius - 1 ,  x[0] + radius - 1] for x in vert]

            mask = pygame.Surface((2 * radius, 2 * radius), pygame.SRCALPHA)
            mask.fill((0, 0, 0, 0))
            pygame.draw.polygon(mask, (255, 255, 255, alpha), vertices)

        if is_interactive:
            texture_surface = pygame.transform.scale(self.texture_surface, (2 * int(self.interaction_radius),
                                                                            2 * int(self.interaction_radius)))
        else:
            texture_surface = self.texture_surface.copy()

        texture_surface = pygame.transform.rotate(texture_surface, 180*self.pm_body.angle/math.pi)
        delta = ((2 * radius + 1) - texture_surface.get_width(), (2 * radius + 1) - texture_surface.get_height())

        delta = (delta[0]/2, delta[1]/2)

        mask.blit(texture_surface, delta, None, pygame.BLEND_MULT)

        return mask

    def draw(self, surface, draw_interaction=False, force_recompute_mask=False):
        """
        Draw the obstacle on the environment screen
        """

        if self.prev_angle != self.pm_body.angle or force_recompute_mask:

            self.visible_mask = self.create_mask()

            if self.interactive:
                self.interaction_mask = self.create_mask(is_interactive=True)

            if self.graspable:
                self.grasp_mask = self.create_mask(is_interactive=True)

            self.prev_angle = self.pm_body.angle

        if draw_interaction and self.interactive:

            mask_rect = self.interaction_mask.get_rect()
            mask_rect.center = self.pm_body.position[1], self.pm_body.position[0]
            surface.blit(self.interaction_mask, mask_rect, None)

        if self.visible:

            mask_rect = self.visible_mask.get_rect()
            mask_rect.center = self.pm_body.position[1], self.pm_body.position[0]
            surface.blit(self.visible_mask, mask_rect, None)

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
