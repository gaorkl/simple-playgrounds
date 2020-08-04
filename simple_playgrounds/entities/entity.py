"""
Module that defines Base Class Entity
"""

import math
from abc import ABC
import numpy, cv2

import pymunk
import pygame

from simple_playgrounds.utils.position_utils import PositionAreaSampler, Trajectory
from simple_playgrounds.entities.texture import TextureGenerator, Texture
from simple_playgrounds.utils.definitions import geometric_shapes, CollisionTypes

#pylint: disable=line-too-long
#pylint: disable=too-many-instance-attributes

class Entity(ABC):
    """
    Entity creates a physical object, and deals with interactive properties and visual appearance
    """

    visible = True
    interactive = False
    movable = False
    graspable = False

    index_entity = 0
    entity_type = None

    def __init__(self, initial_position=None, **entity_params):
        """ Base class for entities.

        Args:
            initial_position: Can be list, tuple (x,y,theta), Trajectory or PositionAreaSampler instances
            **entity_params: Additional Keyword Arguments

        Keyword Args:
            name (str): Name of the entity. If none is provided, name is generated automatically.
            graspable (:obj:'bool'): True if the object can be grasped by an agent.
                Default: False.
            movable (:obj:'bool'): True if the object can be moved
                Default: False.
            interaction_range (:obj:'int'): Size of the interaction area.
            texture: dictionary of texture parameters. Refer to the class Texture
            is_temporary_entity (:obj:'bool'): if True, object doesn't re-appear after playground reset.
                Default: False.
            physical_shape (str): shape of the entity.
                Can be 'circle', 'square', 'rectangle', 'pentagon', 'hexagon'.
            width_length: tuple of width, length to be set for rectangle shapes.
            radius (:obj: 'float'): radius for non-rectangle shapes.
            mass (:obj: 'float'): mass of the entity.
        """

        # Internal counter to assign identity number and name to each entity
        self.name = entity_params.get('name', self.entity_type + '_' + str(Entity.index_entity))
        Entity.index_entity += 1

        self.interaction_range = entity_params.get('interaction_range', 5)

        self.physical_shape, self.mass, visible_size, interaction_size = self._get_physical_properties(entity_params)

        self.length, self.width, self.radius = visible_size
        self.interaction_length, self.interaction_width, self.interaction_radius = interaction_size

        self.pm_body = self._create_pm_body()
        self.pm_elements = [self.pm_body]

        self.texture_surface = self._create_texture(entity_params['texture'])

        self.pm_interaction_shape = None
        self.pm_visible_shape = None

        if self.visible:
            self.pm_visible_shape = self._create_pm_shape()
            self.visible_mask = self._create_mask()
            self.pm_elements.append(self.pm_visible_shape)

        if self.interactive:
            self.pm_interaction_shape = self._create_pm_shape(is_interactive=True)
            self.interaction_mask = self._create_mask(is_interactive=True)
            self.pm_elements.append(self.pm_interaction_shape)

        if self.graspable:
            self.pm_grasp_shape = self._create_pm_shape(is_interactive=True)
            self.pm_grasp_shape.collision_type = CollisionTypes.GRASPABLE
            self.grasp_mask = self._create_mask(is_interactive=True)
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

        # Used to set an element which is not supposed to overlap
        self.allow_overlapping = entity_params.get('allow_overlapping', True)

    def _get_physical_properties(self, params):

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

    def _create_texture(self, texture_params):

        if isinstance(texture_params, Texture):
            texture = texture_params

        else:
            if isinstance(texture_params, (list, tuple)):
                texture_params = {'texture_type': 'color', 'color': texture_params}

            texture_params['radius'] = self.radius
            texture = TextureGenerator.create(texture_params)

        texture_surface = texture.generate()

        return texture_surface

    @property
    def initial_position(self):
        """
        Initial position of the Entity. Can be list, tuple, or PositionAreaSampler object
        """

        if isinstance(self._initial_position, (list, tuple)):
            return self._initial_position

        if isinstance(self._initial_position, PositionAreaSampler):
            return self._initial_position.sample()

        raise ValueError

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
        '''
        Position (x, y, orientation) of the Entity
        '''

        pm_x, pm_y = self.pm_body.position
        phi = self.pm_body.angle

        coord_x = self.size_playground[0] - pm_y
        coord_y = pm_x
        coord_phi = (phi + math.pi / 2) % (2 * math.pi)

        return coord_x, coord_y, coord_phi

    @position.setter
    def position(self, pos):

        coord_x, coord_y, coord_phi = pos

        # make sure that coordinates are within playground
        coord_x = max(min(self.size_playground[0], coord_x), 0)
        coord_y = max(min(self.size_playground[1], coord_y), 0)

        pos_y = self.size_playground[0] - coord_x
        pos_x = coord_y
        phi = coord_phi - math.pi / 2

        if self.physical_shape not in ['rectangle', 'circle']:
            phi = phi + math.pi / geometric_shapes[self.physical_shape]

        self.pm_body.position = pos_x, pos_y
        self.pm_body.angle = phi

    @property
    def velocity(self):
        """
        Velocity of the Entity
        """
        v_x, v_y = self.pm_body.velocity
        v_phi = self.pm_body.angular_velocity

        v_x, v_y = -v_y, v_x
        return v_x, v_y, v_phi

    @velocity.setter
    def velocity(self, vel):
        v_x, v_y, v_phi = vel

        self.pm_body.velocity = (-v_y, v_x)
        self.pm_body.angular_velocity = v_phi

    @property
    def relative_velocity(self):

        abs_vel_x, abs_vel_y, abs_ang_vel = self.velocity
        _, _, angle = self.position

        rel_vel_x = abs_vel_x * math.cos(angle) + abs_vel_y * math.cos(angle - math.pi / 2)
        rel_vel_y = abs_vel_x * math.sin(angle) + abs_vel_y * math.sin(angle - math.pi / 2)

        return rel_vel_x, rel_vel_y, abs_ang_vel

    def _create_pm_body(self):

        if self.movable:
            inertia = self._compute_moments()
            pm_body = pymunk.Body(self.mass, inertia)

        else:
            pm_body = pymunk.Body(body_type=pymunk.Body.STATIC)

        return pm_body

    def _compute_moments(self):

        if self.physical_shape == 'circle':
            moment = pymunk.moment_for_circle(self.mass, 0, self.radius)

        elif self.physical_shape in ['triangle', 'square', 'pentagon', 'hexagon']:
            vertices = self._compute_vertices(angle=0)
            moment = pymunk.moment_for_poly(self.mass, vertices)

        elif self.physical_shape == 'rectangle':
            moment = pymunk.moment_for_box(self.mass, (self.width, self.length))

        else:
            raise ValueError('Not implemented')

        return moment

    def _compute_vertices(self, angle, is_interactive=False, border=0):

        vertices = []

        if self.physical_shape == 'rectangle':

            if is_interactive:
                width = self.interaction_width + border
                length = self.interaction_length + border
            else:
                width = self.width + border
                length = self.length + border

            coord_pts_in_entity_base = [[width/2., length/2.], [-width/2.-1, length/2.],
                                        [-width/2.-1, -length/2.-1], [width/2., -length/2.-1]]

            for coord in coord_pts_in_entity_base:

                pos_x = coord[0] * math.cos(angle) - coord[1] * math.sin(angle)
                pos_y = coord[0] * math.sin(angle) + coord[1] * math.cos(angle)

                vertices.append([pos_x, pos_y])
        else:
            if is_interactive:
                radius = self.interaction_radius + border
            else:
                radius = self.radius + border

            number_sides = geometric_shapes[self.physical_shape]

            for n_sides in range(number_sides):
                vertices.append([radius*math.cos(n_sides * 2*math.pi / number_sides + angle),
                                 radius * math.sin(n_sides * 2*math.pi / number_sides + angle)])

        return vertices

    def _create_pm_shape(self, is_interactive=False):

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
            vertices = self._compute_vertices(angle=self.pm_body.angle, is_interactive=is_interactive)
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

    def _create_mask(self, is_interactive=False):

        #pylint: disable-all

        delta = (0, 0)

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

        elif self.physical_shape == 'rectangle':

            vert = self._compute_vertices(angle=self.pm_body.angle, is_interactive=is_interactive, border=0)
            vertices = [[x[1] + radius , x[0] + radius ] for x in vert]

            mask = pygame.Surface((2 * radius, 2 * radius), pygame.SRCALPHA)
            mask.fill((0, 0, 0, 0))
            pygame.draw.polygon(mask, (255, 255, 255, alpha), vertices)

        else:

            vert = self._compute_vertices(angle=self.pm_body.angle, is_interactive=is_interactive, border=0)
            vertices = [[x[1] + radius , x[0] + radius ] for x in vert]

            mask = pygame.Surface((2 * radius+2, 2 * radius+2), pygame.SRCALPHA)
            mask.fill((0, 0, 0, 0))
            pygame.draw.polygon(mask, (255, 255, 255, alpha), vertices)


        if is_interactive:
            texture_surface = pygame.transform.scale(self.texture_surface, (2 * int(self.interaction_radius),
                                                                            2 * int(self.interaction_radius)))

            texture_surface = pygame.transform.rotate(texture_surface, self.pm_body.angle * 180 / math.pi)
            mask_rect = texture_surface.get_rect()
            mask_rect.center = self.interaction_radius, self.interaction_radius
            mask.blit(texture_surface, mask_rect, None, pygame.BLEND_MULT)
        else:
            texture_surface = self.texture_surface.copy()
            texture_surface = pygame.transform.rotate(texture_surface, self.pm_body.angle * 180 / math.pi)
            mask_rect = texture_surface.get_rect()
            mask_rect.center = self.radius, self.radius
            mask.blit(texture_surface, mask_rect, None, pygame.BLEND_MULT)

        return mask


    def draw(self, surface, draw_interaction=False, force_recompute_mask=False):
        """
        Draw the obstacle on the environment screen
        """

        if self.prev_angle != self.pm_body.angle or force_recompute_mask:

            self.visible_mask = self._create_mask()

            if self.interactive:
                self.interaction_mask = self._create_mask(is_interactive=True)

            if self.graspable:
                self.grasp_mask = self._create_mask(is_interactive=True)

            self.prev_angle = self.pm_body.angle

        if draw_interaction and self.interactive:

            mask_rect = self.interaction_mask.get_rect()
            mask_rect.center = self.pm_body.position[1], self.pm_body.position[0]
            surface.blit(self.interaction_mask, mask_rect, None)

        if self.visible:

            mask_rect = self.visible_mask.get_rect()
            mask_rect.center = self.pm_body.position[1], self.pm_body.position[0]
            surface.blit(self.visible_mask, mask_rect, None)

    def pre_step(self):
        """
        Performs calculation before the physical environment steps.
        """

        if self.follows_waypoints:
            self.position = next(self.trajectory)

    def reset(self):
        """
        Reset the trajectory and initial position
        """

        if self.follows_waypoints:
            self.trajectory.reset()

        self.velocity = [0, 0, 0]
        self.position = self.initial_position
