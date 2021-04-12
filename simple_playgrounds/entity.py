""" Contains the base class for entities.

Entity class should be used to create body parts of
an agent, or scene entities.
Entity is the generic building block of physical and interactive
objects in simple-playgrounds.

Examples can be found in :
    - simple_playgrounds/agents/parts
    - simple_playgrounds/playgrounds/scene_elements
"""
import math
from abc import ABC

import pymunk
import pygame

from simple_playgrounds.utils.position_utils import CoordinateSampler, Trajectory
from simple_playgrounds.utils.texture import TextureGenerator, Texture
from simple_playgrounds.utils.definitions import geometric_shapes, CollisionTypes

# pylint: disable=line-too-long
# pylint: disable=too-many-instance-attributes

FRICTION_ENTITY = 0.8
ELASTICITY_ENTITY = 0.5


class Entity(ABC):
    """
    Entity creates a physical object, and deals with interactive properties and visual appearance
    """

    visible = True
    traversable = False
    interactive = False
    movable = False
    graspable = False

    index_entity = 0
    entity_type = None
    entity_number = None

    drawn = False

    follows_waypoints = False

    def __init__(self, **entity_params):
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
        self.name = entity_params.get('name', self.entity_type.name.lower() + '_' + str(Entity.index_entity))
        Entity.index_entity += 1

        self.interaction_range = entity_params.get('interaction_range', 5)

        self.physical_shape, self.mass, visible_size, interaction_size = self._get_physical_properties(entity_params)

        self.length, self.width, self.radius = visible_size
        self.interaction_length, self.interaction_width, self.interaction_radius = interaction_size

        self.pm_body = self._create_pm_body()
        self.pm_elements = [self.pm_body]

        # To be set when entity is added to playground. Used to calculate correct coordinates

        self._initial_coordinates = None

        # Texture random generator can be set
        self.texture_rng = entity_params.get('')
        self.texture_surface = self._create_texture(entity_params['texture'])

        self.trajectory = None

        self.pm_visible_shape = None
        self.pm_interaction_shape = None
        self.pm_visible_shape = None
        self.pm_grasp_shape = None

        if self.visible:
            self.pm_visible_shape = self._create_pm_shape()
            self.pm_elements.append(self.pm_visible_shape)

            # traversable don't collide with other scene elements.
            self.reset_mask_shape_filter()

        if self.interactive:
            self.pm_interaction_shape = self._create_pm_shape(is_interactive=True)
            self.pm_elements.append(self.pm_interaction_shape)

        if self.graspable:
            self.pm_grasp_shape = self._create_pm_shape(is_interactive=True)
            self.pm_grasp_shape.collision_type = CollisionTypes.GRASPABLE
            self.pm_elements.append(self.pm_grasp_shape)

        self.grasp_mask = None
        self.interaction_mask = None
        self.visible_mask = None

        # To remove temporary entities when reset
        self.is_temporary_entity = entity_params.get('is_temporary_entity', False)

        # Used to check if mask should be computed again
        self.prev_angle = self.pm_body.angle

        # Used to set an element which is not supposed to overlap
        self._allow_overlapping = False
        self._overlapping_strategy_set = False
        self._max_attempts = 100
        self._error_if_fails = False

        for prop, value in entity_params.get('pm_attr', {}).items():
            self._set_pm_attr(prop, value)

        background = entity_params.get('background', False)
        assert isinstance(background, bool)
        self.background = background

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

    def _set_pm_attr(self, prop, value):
        for pm_elem in self.pm_elements:
            setattr(pm_elem, prop, value)

    def update_mask_shape_filter(self, category_index):
        """
        Used to define collisions between entities.
        Used for sensors.

        Returns:

        """
        if self.pm_visible_shape is not None:
            mask_filter = self.pm_visible_shape.filter.mask ^ 2**category_index
            self.pm_visible_shape.filter = pymunk.ShapeFilter(categories=self.pm_visible_shape.filter.categories,
                                                              mask=mask_filter)

    def reset_mask_shape_filter(self):
        if self.traversable:
            self.pm_visible_shape.filter = pymunk.ShapeFilter(categories=1)
        else:
            self.pm_visible_shape.filter = pymunk.ShapeFilter(categories=2, mask=pymunk.ShapeFilter.ALL_MASKS() ^ 1)

    # BODY AND SHAPE

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
            vertices = self._compute_vertices()
            moment = pymunk.moment_for_poly(self.mass, vertices)

        elif self.physical_shape == 'rectangle':
            moment = pymunk.moment_for_box(self.mass, (self.width, self.length))

        else:
            raise ValueError('Not implemented')

        return moment

    def _compute_vertices(self, offset_angle=0., is_interactive=False):

        vertices = []

        if self.physical_shape == 'rectangle':

            if is_interactive:
                width = self.interaction_width
                length = self.interaction_length
            else:
                width = self.width
                length = self.length

            coord_pts_in_entity_base = [(width / 2., length / 2.), (width / 2., -length / 2.),
                                        (-width / 2., -length / 2.), (-width / 2., length / 2.)]

            for coord in coord_pts_in_entity_base:
                pos_x = coord[0] * math.cos(offset_angle) - coord[1] * math.sin(offset_angle)
                pos_y = coord[0] * math.sin(offset_angle) + coord[1] * math.cos(offset_angle)

                vertices.append((pos_x, pos_y))
        else:
            if is_interactive:
                radius = self.interaction_radius
            else:
                radius = self.radius

            number_sides = geometric_shapes[self.physical_shape]

            for n_sides in range(number_sides):
                vertices.append((radius * math.cos(n_sides * 2 * math.pi / number_sides + offset_angle),
                                 radius * math.sin(n_sides * 2 * math.pi / number_sides + offset_angle)))

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
            vertices = self._compute_vertices(is_interactive=is_interactive)
            pm_shape = pymunk.Poly(self.pm_body, vertices)

        elif self.physical_shape == 'rectangle':
            pm_shape = pymunk.Poly.create_box(self.pm_body, (width, length))

        else:
            raise ValueError

        if is_interactive:
            pm_shape.sensor = True
        else:
            pm_shape.friction = FRICTION_ENTITY
            pm_shape.elasticity = ELASTICITY_ENTITY

        return pm_shape

    # VISUAL APPEARANCE

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

    def _create_mask(self, is_interactive=False):

        # pylint: disable-all

        if is_interactive:
            radius = self.interaction_radius
            alpha = 75
        else:
            radius = self.radius
            alpha = 255

        mask = pygame.Surface((int(2 * radius) + 1, int(2 * radius) + 1), pygame.SRCALPHA)
        mask.fill((0, 0, 0, 0))

        if self.physical_shape == 'circle':
            pygame.draw.circle(mask, (255, 255, 255, alpha), (int(radius), int(radius)), int(radius))

        else:
            vert = self._compute_vertices(offset_angle=self.angle, is_interactive=is_interactive)
            vertices = [[x[0] + radius, x[1] + radius] for x in vert]
            pygame.draw.polygon(mask, (255, 255, 255, alpha), vertices)

        if is_interactive:
            texture_surface = pygame.transform.scale(self.texture_surface,
                                                     (2 * int(self.interaction_radius) + 1,
                                                      2 * int(self.interaction_radius) + 1))
        else:
            texture_surface = self.texture_surface.copy()

        # Pygame / numpy conversion
        mask_angle = math.pi/2 - self.angle
        texture_surface = pygame.transform.rotate(texture_surface, mask_angle * 180 / math.pi)
        mask_rect = texture_surface.get_rect()
        mask_rect.center = radius, radius
        mask.blit(texture_surface, mask_rect, None, pygame.BLEND_MULT)

        return mask

    # OVERLAPPING STRATEGY
    @property
    def overlapping_strategy(self):
        if self._overlapping_strategy_set:
            return self._allow_overlapping, self._max_attempts, self._error_if_fails

        else:
            return None

    @overlapping_strategy.setter
    def overlapping_strategy(self, strategy):
        self._allow_overlapping, self._max_attempts, self._error_if_fails = strategy
        self._overlapping_strategy_set = False


    # POSITION AND VELOCITY

    @property
    def initial_coordinates(self):
        """
        Initial coordinates of the Entity.
        Can be tuple of (x,y), angle, or PositionAreaSampler object
        """

        if isinstance(self._initial_coordinates, (tuple, list)):
            return self._initial_coordinates

        elif isinstance(self._initial_coordinates, CoordinateSampler):
            return self._initial_coordinates.sample()

        raise ValueError

    @initial_coordinates.setter
    def initial_coordinates(self, init_coordinates):

        if isinstance(init_coordinates, Trajectory):
            self.trajectory = init_coordinates
            self._initial_coordinates = next(self.trajectory)
            self.follows_waypoints = True

        elif isinstance(init_coordinates, (tuple, list, CoordinateSampler)):
            self._initial_coordinates = init_coordinates

        else:
            raise ValueError('Initial position not valid')

    @property
    def coordinates(self):
        return self.position, self.angle

    @property
    def position(self):
        return self.pm_body.position

    @position.setter
    def position(self, pos):
        self.pm_body.position = pos

    @property
    def angle(self):
        return self.pm_body.angle

    @angle.setter
    def angle(self, phi):
        self.pm_body.angle = phi

    @property
    def velocity(self):
        return self.pm_body.velocity

    @velocity.setter
    def velocity(self, vel):
        self.pm_body.velocity = vel

    @property
    def angular_velocity(self):
        return self.pm_body.angular_velocity

    @angular_velocity.setter
    def angular_velocity(self, v_phi):
        self.pm_body.angular_velocity = v_phi

    # INTERFACE

    def pre_step(self):
        """
        Performs calculation before the physical environment steps.
        """

        if self.follows_waypoints:
            self.position, self.angle = next(self.trajectory)

        if not self.background:
            self.drawn = False

    def reset(self):
        """
        Reset the trajectory and initial position
        """

        if self.follows_waypoints:
            self.trajectory.reset()

        self.velocity = (0, 0)
        self.angular_velocity = 0
        
        self.position, self.angle = self.initial_coordinates

        self.drawn = False

    def draw(self, surface, draw_interaction=False, force_recompute_mask=False):
        """
        Draw the entity on the surface.

        Args:
            surface: Pygame Surface.
            draw_interaction: If True and Entity is interactive, draws the interactive area.
            force_recompute_mask: If True, the visual appearance is re-calculated.
        """

        draw_mask = False

        if draw_interaction and self.interaction_mask is None:
            draw_mask = True

        if self.visible_mask is None:
            draw_mask = True

        if self.prev_angle != self.pm_body.angle or force_recompute_mask:
            draw_mask = True

        if draw_mask:

            self.visible_mask = self._create_mask()

            if self.interactive:
                self.interaction_mask = self._create_mask(is_interactive=True)

            if self.graspable:
                self.grasp_mask = self._create_mask(is_interactive=True)

            self.prev_angle = self.pm_body.angle

        if draw_interaction and self.interactive:

            mask_rect = self.interaction_mask.get_rect()
            mask_rect.center = self.pm_body.position[0], self.pm_body.position[1]
            surface.blit(self.interaction_mask, mask_rect, None)

        if self.visible:

            mask_rect = self.visible_mask.get_rect()
            mask_rect.center = self.pm_body.position[0], self.pm_body.position[1]
            surface.blit(self.visible_mask, mask_rect, None)

        self.drawn = True
