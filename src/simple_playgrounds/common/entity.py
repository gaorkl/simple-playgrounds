""" Contains the base class for entities.

Entity class should be used to create body parts of
an agent, or scene entities.
Entity is the generic building block of physical and interactive
objects in simple-playgrounds.

Examples can be found in :
    - simple_playgrounds/agents/parts
    - simple_playgrounds/playgrounds/scene_elements
"""
import numbers
from enum import IntEnum, auto
from typing import Union, Tuple, Dict, List, Optional

import math
from abc import ABC, abstractmethod

import pymunk
import pygame
from simple_playgrounds.common.definitions import FRICTION_ENTITY, ELASTICITY_ENTITY, CollisionTypes

from .position_utils import CoordinateSampler, Trajectory, InitCoord, Coordinate
from .texture import Texture, TextureGenerator, ColorTexture


# pylint: disable=line-too-long
# pylint: disable=too-many-instance-attributes


class Entity(ABC):
    """
    Entity creates a physical object, and deals with interactive properties and visual appearance
    """

    index_entity = 0

    def __init__(
        self,
        visible_shape: bool,
        invisible_shape: bool,
        texture: Union[Texture, Dict, Tuple[int, int, int]],
        physical_shape: str,
        size: Optional[Tuple[float, float]] = None,
        radius: Optional[float] = None,
        invisible_range: float = 5,
        graspable: bool = False,
        traversable: bool = False,
        movable: bool = False,
        temporary: bool = False,
        name: Optional[str] = None,
        mass: Optional[float] = None,
        generate_texture: bool = True,
        background: bool = True,
        **pymunk_attributes,
    ):

        # Internal counter to assign identity number and name to each entity
        self.name: str

        if not name:
            self.name = self.__class__.__name__ + '_' + str(
                Entity.index_entity)
        else:
            assert isinstance(name, str)
            self.name = name
        Entity.index_entity += 1

        # Physical properties of the entity
        if graspable:
            movable = True

        if movable:
            assert mass
        self.mass = mass
        self.physical_shape = PhysicalShapes[physical_shape.upper()]

        # Dimensions of the entity
        self._invisible_range = invisible_range
        self._size_visible: Union[Tuple[float, float], List[float]]

        if radius and not size:
            assert isinstance(radius, (float, int))
            self._radius_visible = radius
            self._size_visible = (2 * radius, 2 * radius)
            self._radius_invisible = radius + self._invisible_range
            self._size_invisible = (2 * self._radius_invisible,
                                    2 * self._radius_invisible)

        elif size and not radius:
            assert len(size) == 2

            width, length = size
            self._size_visible = size
            self._radius_visible = ((width / 2.)**2 + (length / 2.)**2)**(1 /
                                                                          2.)
            self._size_invisible = width + self._invisible_range, length + self._invisible_range
            self._radius_invisible = self._radius_visible + self._invisible_range

        else:
            raise ValueError("Either size or radius should be set (not both).")

        self.pm_body = self._create_pm_body(movable)
        self.pm_elements = [self.pm_body]

        self.pm_visible_shape = None
        self.pm_invisible_shape = None
        self.pm_grasp_shape = None

        if visible_shape:
            self.pm_visible_shape = self._create_pm_shape()
            self.pm_elements.append(self.pm_visible_shape)

            if traversable:
                self.pm_visible_shape.filter = pymunk.ShapeFilter(categories=1)
            else:
                self.pm_visible_shape.filter = pymunk.ShapeFilter(
                    categories=2, mask=pymunk.ShapeFilter.ALL_MASKS() ^ 1)

        # Interactive properties of the entity

        if invisible_shape:
            self.pm_invisible_shape = self._create_pm_shape(invisible=True)
            self.pm_elements.append(self.pm_invisible_shape)

        if graspable:
            self.pm_grasp_shape = self._create_pm_shape(invisible=True)
            self.pm_grasp_shape.collision_type = CollisionTypes.GRASPABLE
            self.pm_elements.append(self.pm_grasp_shape)

        self._set_shape_collision()

        # To be set when entity is added to playground.
        self._initial_coordinates: Optional[InitCoord] = None
        self.trajectory: Optional[Trajectory] = None

        # Texture random generator can be set
        if isinstance(texture, Dict):
            texture['size'] = self._size_visible
            texture = TextureGenerator.create(**texture)

        elif isinstance(texture, (tuple, list)):
            texture = ColorTexture(size=self._size_visible, color=texture)

        assert isinstance(texture, Texture)

        self.texture: Texture = texture
        if generate_texture:
            self._texture_surface = self.texture.generate()
        else:
            self._texture_surface = self.texture.surface

        # Used to set an element which is not supposed to overlap
        self._allow_overlapping = False
        self._overlapping_strategy_set = False
        self._max_attempts = 100

        self._set_pm_attr(pymunk_attributes)

        if invisible_shape or movable:
            background = False

        self.background = background
        self.movable = movable
        self.graspable = graspable
        self.drawn = False

        self.temporary = temporary

    def get_pixel(self, relative_pos):

        return self.texture.get_pixel(relative_pos)

    @property
    def base_color(self):
        return self.texture.base_color

    @property
    def radius(self):
        return self._radius_visible

    @property
    def size(self):
        return self._size_visible

    @abstractmethod
    def _set_shape_collision(self):
        pass

    def assign_shape_filter(self,
                            category_index: int,
                            ):
        """
        Used to define collisions between entities.
        Used for sensors.

        Returns:

        """
        if self.pm_visible_shape is not None:
            mask_filter = self.pm_visible_shape.filter.mask ^ 2**category_index
            self.pm_visible_shape.filter = pymunk.ShapeFilter(
                categories=self.pm_visible_shape.filter.categories,
                mask=mask_filter)

    def _set_pm_attr(self, attr):

        for prop, value in attr.items():
            for pm_elem in self.pm_elements:
                setattr(pm_elem, prop, value)

    # BODY AND SHAPE

    def _create_pm_body(self,
                        movable: bool,
                        ):

        if not movable:
            return pymunk.Body(body_type=pymunk.Body.STATIC)

        assert isinstance(self.mass, (float, int))

        if self.physical_shape == PhysicalShapes.CIRCLE:
            moment = pymunk.moment_for_circle(self.mass, 0,
                                              self._radius_visible)

        elif self.physical_shape in [
                PhysicalShapes.TRIANGLE, PhysicalShapes.SQUARE,
                PhysicalShapes.PENTAGON, PhysicalShapes.HEXAGON
        ]:

            vertices = self._compute_vertices()
            moment = pymunk.moment_for_poly(self.mass, vertices)

        elif self.physical_shape == PhysicalShapes.RECTANGLE:
            shape = self._size_visible[1], self._size_visible[0]
            moment = pymunk.moment_for_box(self.mass, shape)

        else:
            raise ValueError

        return pymunk.Body(self.mass, moment)

    def _compute_vertices(self, offset_angle=0., invisible=False):

        vertices = []

        if self.physical_shape == PhysicalShapes.RECTANGLE:

            width, length = self._size_visible
            if invisible:
                width, length = self._size_invisible

            points = [
                pymunk.Vec2d(width / 2., length / 2.),
                pymunk.Vec2d(width / 2., -length / 2.),
                pymunk.Vec2d(-width / 2., -length / 2.),
                pymunk.Vec2d(-width / 2., length / 2.)
            ]

            for pt in points:
                pt_rotated = pt.rotated(offset_angle)
                vertices.append(pt_rotated)

            return vertices

        else:

            radius = self._radius_visible
            if invisible:
                radius = self._radius_invisible

            number_sides = self.physical_shape.value

            orig = pymunk.Vec2d(radius, 0)

            for n_sides in range(number_sides):
                vertices.append(
                    orig.rotated(n_sides * 2 * math.pi / number_sides +
                                 offset_angle))

        return vertices

    def _create_pm_shape(self, invisible=False):

        if self.physical_shape == PhysicalShapes.CIRCLE:

            if invisible:
                pm_shape = pymunk.Circle(self.pm_body, self._radius_invisible)
            else:
                pm_shape = pymunk.Circle(self.pm_body, self._radius_visible)

        elif self.physical_shape in [
                PhysicalShapes.TRIANGLE, PhysicalShapes.SQUARE,
                PhysicalShapes.PENTAGON, PhysicalShapes.HEXAGON
        ]:

            vertices = self._compute_vertices(invisible=invisible)
            pm_shape = pymunk.Poly(self.pm_body, vertices)

        elif self.physical_shape == PhysicalShapes.RECTANGLE:

            if invisible:
                pm_shape = pymunk.Poly.create_box(self.pm_body,
                                                  self._size_invisible)
            else:
                pm_shape = pymunk.Poly.create_box(self.pm_body,
                                                  self._size_visible)
        else:
            raise ValueError

        if invisible:
            pm_shape.sensor = True
        else:
            pm_shape.friction = FRICTION_ENTITY
            pm_shape.elasticity = ELASTICITY_ENTITY

        return pm_shape

    # VISUAL APPEARANCE

    def _create_mask(self, invisible=False):

        # pylint: disable-all

        alpha = 255
        mask_size = (2 * self._radius_visible, 2 * self._radius_visible)
        center = self._radius_visible, self._radius_visible

        if invisible:
            alpha = 75
            mask_size = (2 * self._radius_invisible,
                         2 * self._radius_invisible)
            center = self._radius_invisible, self._radius_invisible

        mask_size = int(mask_size[0]), int(mask_size[1])
        mask = pygame.Surface(mask_size, pygame.SRCALPHA)
        mask.fill((0, 0, 0, 0))

        if self.physical_shape == PhysicalShapes.CIRCLE:
            radius = center[0]
            pygame.draw.circle(mask, (255, 255, 255, alpha), center, radius)

        else:
            vert = self._compute_vertices(offset_angle=self.angle,
                                          invisible=invisible)
            vertices = [v - v.normalized() + center for v in vert]
            pygame.draw.polygon(mask, (255, 255, 255, alpha), vertices)

        if invisible:
            texture_surface = pygame.transform.scale(self._texture_surface,
                                                     mask_size)
        else:
            texture_surface = self._texture_surface.copy()

        # Pygame / numpy conversion
        mask_angle = math.pi / 2 - self.angle
        texture_surface = pygame.transform.rotate(texture_surface,
                                                  mask_angle * 180 / math.pi)
        mask_rect = texture_surface.get_rect()
        mask_rect.center = center
        if self.physical_shape == PhysicalShapes.RECTANGLE:
            mask_rect.center = center[0] + 1, center[1] + 1
        mask.blit(texture_surface, mask_rect, None, pygame.BLEND_MULT)

        return mask

    # OVERLAPPING STRATEGY
    @property
    def overlapping_strategy(self):
        if self._overlapping_strategy_set:
            return self._allow_overlapping, self._max_attempts

        else:
            return None

    @overlapping_strategy.setter
    def overlapping_strategy(self, strategy):
        self._allow_overlapping, self._max_attempts = strategy
        self._overlapping_strategy_set = True

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
    def initial_coordinates(self, init_coordinates: InitCoord):

        if isinstance(init_coordinates, Trajectory):
            self.trajectory = init_coordinates
            self._initial_coordinates = next(self.trajectory)

        else:
            if not isinstance(init_coordinates, CoordinateSampler):
                assert len(init_coordinates) == 2 and len(init_coordinates[0]) == 2
            self._initial_coordinates = init_coordinates

    @property
    def coordinates(self):
        return self.position, self.angle

    @coordinates.setter
    def coordinates(self, coord: Coordinate):

        assert len(coord) == 2 and len(coord[0]) == 2
        self.position, self.angle = coord
        if self.pm_body.space:
            self.pm_body.space.reindex_shapes_for_body(self.pm_body)

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

        if self.trajectory:
            self.position, self.angle = next(self.trajectory)

        if not self.background:
            self.drawn = False

    def reset(self):
        """
        Reset the trajectory and initial position
        """

        if self.trajectory:
            self.trajectory.reset()

        self.velocity = (0, 0)
        self.angular_velocity = 0

        self.position, self.angle = self.initial_coordinates

        self.drawn = False

    def draw(self, surface, draw_invisible=False, force_recompute_mask=False):
        """
        Draw the entity on the surface.

        Args:
            surface: Pygame Surface.
            draw_invisible: If True, draws invisible shape
            force_recompute_mask: If True, the visual appearance is re-calculated.
        """

        if draw_invisible and (self.pm_invisible_shape or self.pm_grasp_shape):
            invisible_mask = self._create_mask(invisible=True)
            mask_rect = invisible_mask.get_rect()
            mask_rect.center = self.position
            surface.blit(invisible_mask, mask_rect, None)

        if self.pm_visible_shape:
            visible_mask = self._create_mask()
            mask_rect = visible_mask.get_rect()
            mask_rect.center = self.position
            surface.blit(visible_mask, mask_rect, None)

        self.drawn = True


class PhysicalShapes(IntEnum):

    LINE = 2
    TRIANGLE = 3
    SQUARE = 4
    PENTAGON = 5
    HEXAGON = 6
    CIRCLE = 60
    RECTANGLE = auto()
