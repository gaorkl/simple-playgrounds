import math
from abc import ABC, abstractmethod
from typing import Optional, Dict, Tuple, Union, TYPE_CHECKING
if TYPE_CHECKING:
    from simple_playgrounds.common.position_utils import Trajectory, InitCoord

import pygame

import numpy as np
import pymunk
import math


from simple_playgrounds.entity.entity import Entity
from simple_playgrounds.common.position_utils import CoordinateSampler, Coordinate
from simple_playgrounds.common.definitions import MAX_ATTEMPTS_OVERLAPPING, GeometricShapes
from simple_playgrounds.common.texture import Texture, TextureGenerator, ColorTexture
from simple_playgrounds.common.definitions import ALPHA_VISIBLE, ALPHA_INVISIBLE


class EmbodiedEntity(Entity, ABC):

    def __init__(self,
                 physical_shape: str,
                 movable: bool = False,
                 mass: Optional[float] = None,
                 size: Optional[Tuple[float, float]] = None,
                 radius: Optional[float] = None,
                 vertices: Optional[float] = None,
                 **kwargs
                 ):

        super().__init__(**kwargs)

        if movable:
            assert mass

        self._physical_shape = GeometricShapes[physical_shape.upper()]
        assert self._physical_shape in [i for i in GeometricShapes]

        self._radius, self._size, self._vertices = self._compute_sizes(size, radius, vertices)

        self.pm_body = self._create_pm_body(movable)
        self.pm_elements = [self.pm_body]

        # To be set when entity is added to playground.
        self._initial_coordinates: Optional[InitCoord] = None
        self._trajectory: Optional[Trajectory] = None

        # Used to set an element which is not supposed to overlap
        self._allow_overlapping = False
        self._overlapping_strategy_set = False
        self._max_attempts = MAX_ATTEMPTS_OVERLAPPING

    def _compute_sizes(self, size, radius, vertices):

        if self._physical_shape in [
            GeometricShapes.TRIANGLE,
            GeometricShapes.SQUARE,
            GeometricShapes.PENTAGON,
            GeometricShapes.HEXAGON,
            GeometricShapes.CIRCLE,
        ]:
            assert radius is not None and isinstance(radius, (float, int))

            size = (2 * radius, 2 * radius)
            vertices = None

        elif self._physical_shape == GeometricShapes.RECTANGLE:
            assert size is not None and len(size) == 2

            width, length = size
            radius = ((width / 2)**2 + (length / 2)**2)**(1 / 2)
            vertices = None

        elif self._physical_shape == GeometricShapes.POLYGON:
            assert vertices is not None and len(vertices) > 1

            vertices = np.array(vertices)
            center = np.mean(vertices, axis=0)
            vertices = vertices - center

            width = np.max(vertices[:, 0]) - np.min(vertices[:, 0])
            length = np.max(vertices[:, 1]) - np.min(vertices[:, 1])

            radius = ((width / 2)**2 + (length / 2)**2)**(1 / 2)
            size = (2 * radius, 2 * radius)

        else:
            raise ValueError('Wrong physical shape.')

        return radius, size, vertices

    def _create_pm_body(self, movable: bool, mass: Optional[float] = None):

        if not movable:
            return pymunk.Body(body_type=pymunk.Body.STATIC)

        assert isinstance(mass, (float, int))

        if self._physical_shape == GeometricShapes.CIRCLE:
            moment = pymunk.moment_for_circle(mass, 0, self._radius)

        else:
            vertices = self._compute_vertices()
            moment = pymunk.moment_for_poly(mass, vertices)

        return pymunk.Body(mass, moment)

    def _compute_vertices(self,
                          offset_angle: Optional[float] = None,
                          additional_range: Optional[float] = None,
                          ):

        if self._physical_shape == GeometricShapes.RECTANGLE:

            width, length = self._size
            if additional_range:
                width, length = width + additional_range, length + additional_range

            vertices = [
                pymunk.Vec2d(width / 2., length / 2.),
                pymunk.Vec2d(width / 2., -length / 2.),
                pymunk.Vec2d(-width / 2., -length / 2.),
                pymunk.Vec2d(-width / 2., length / 2.)
            ]

        elif self._physical_shape in [
                GeometricShapes.TRIANGLE,
                GeometricShapes.SQUARE,
                GeometricShapes.PENTAGON,
                GeometricShapes.HEXAGON,
        ]:

            radius = self._radius
            if additional_range:
                radius += additional_range

            number_sides = self._physical_shape.value

            orig = pymunk.Vec2d(radius, 0)

            vertices = []
            for n_sides in range(number_sides):
                vertices.append(
                    orig.rotated(n_sides * 2 * math.pi / number_sides))

        elif self._physical_shape == GeometricShapes.POLYGON:
            vertices = [pymunk.Vec2d(x, y) for x, y in self._vertices]

        else:
            raise ValueError

        if offset_angle:
            vertices = [vert.rotated(offset_angle) for vert in vertices]

        return vertices

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
            self._trajectory = init_coordinates
            self._initial_coordinates = next(self._trajectory)

        else:
            if not isinstance(init_coordinates, CoordinateSampler):
                assert len(init_coordinates) == 2 and len(
                    init_coordinates[0]) == 2
            self._initial_coordinates = init_coordinates

    @property
    def coordinates(self):
        return self.position, self.angle

    @coordinates.setter
    def coordinates(self, coord: Coordinate):

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
        return self.pm_body.angle % (2*math.pi)

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

    def pre_step(self):
        """
        Performs calculation before the physical environment steps.
        """

        if self._trajectory:
            self.position, self.angle = next(self._trajectory)

    def _add_to_playground(self):
        self._playground.space.add(*self.pm_elements)

    def _remove_from_playground(self):
        self._playground.space.remove(*self.pm_elements)


class PhysicalShape(ABC, EmbodiedEntity):
    """
    Entity creates a physical object, and deals with interactive properties and visual appearance
    """

    def __init__(self,
                 texture: Union[Texture, Dict, Tuple[int, int, int]],
                 traversable: bool = False,
                 visible: bool = True,
                 ):

        self._pm_visible_shape = self.create_pm_shape()
        self.pm_elements.append(self._pm_visible_shape)

        if traversable:
            self._playground.make_traversable(self)

        if not visible:
            self._playground.make_invisible(self)

        self._texture = self._get_texture(texture)
        self._texture.size = self._size
        self._texture_surface = self._texture.generate()

    # Adding and removing from Playground

    def get_pixel(self, relative_pos):
        return self.texture.get_pixel(relative_pos)

    @property
    def base_color(self):
        return self.texture.base_color

    @property
    def radius(self):
        return self._radius

    def create_pm_shape(self,
                        additional_range: Optional[float] = None,
                        ):

        if self.physical_shape == GeometricShapes.CIRCLE:
            pm_shape = pymunk.Circle(self.pm_body, self._radius + additional_range)

        else:
            vertices = self._compute_vertices(additional_range=additional_range)
            pm_shape = pymunk.Poly(self.pm_body, vertices)

        return pm_shape

    # VISUAL APPEARANCE

    def create_mask(self, visible, additional_range: Optional[float] = None):

        if visible:
            alpha = ALPHA_VISIBLE
        else:
            alpha = ALPHA_INVISIBLE

        # pylint: disable-all
        mask_radius = self._radius + 1 + additional_range

        center = (mask_radius, ) * 2
        mask_size = (int(2 * mask_radius), ) * 2
        mask = pygame.Surface(mask_size, pygame.SRCALPHA)
        mask.fill((0, 0, 0, 0))

        if self.physical_shape == GeometricShapes.CIRCLE:
            pygame.draw.circle(mask, (255, 255, 255, alpha), center,
                               mask_radius)

        else:
            vert = self._compute_vertices(
                offset_angle=self.angle, additional_range = additional_range)
            vertices = [v + center for v in vert]
            pygame.draw.polygon(mask, (255, 255, 255, alpha), vertices)

        texture_surface = self._texture_surface.copy()

        # Pygame / numpy conversion
        mask_angle = math.pi / 2 - self.angle
        texture_surface = pygame.transform.rotate(texture_surface,
                                                  mask_angle * 180 / math.pi)
        mask_rect = texture_surface.get_rect()
        mask_rect.center = center
        mask.blit(texture_surface, mask_rect, None, pygame.BLEND_MULT)

        return mask

    @staticmethod
    def _get_texture(texture):
        if isinstance(texture, Dict):
            texture = TextureGenerator.create(**texture)
        elif isinstance(texture, tuple):
            assert len(texture) == 3
            texture = ColorTexture(color=texture)
        assert isinstance(texture, Texture)
        return texture


    # def draw(self, surface, draw_invisible=False, force_recompute_mask=False):
    #     """
    #     Draw the entity on the surface.
    #
    #     Args:
    #         surface: Pygame Surface.
    #         draw_invisible: If True, draws invisible shape
    #         force_recompute_mask: If True, the visual appearance is re-calculated.
    #     """
    #
    #     if draw_invisible and (self.pm_invisible_shape or self.pm_grasp_shape):
    #         invisible_mask = self._create_mask(invisible=True)
    #         mask_rect = invisible_mask.get_rect()
    #         mask_rect.center = self.position
    #         surface.blit(invisible_mask, mask_rect, None)
    #
    #     if self.pm_visible_shape:
    #         visible_mask = self._create_mask()
    #         mask_rect = visible_mask.get_rect()
    #         mask_rect.center = self.position
    #         surface.blit(visible_mask, mask_rect, None)
    #
    #     self.drawn = True


class InteractionShape(ABC, PhysicalShape):

    def __init__(self,
                 invisible_range,
                 texture: Optional[Union[Texture, Dict, Tuple[int, int, int]]] = None
                 ):

        pm_invisible_shape = self.create_pm_shape(additional_range=invisible_range)
        self._set_pm_collision_type(pm_invisible_shape)

        self.pm_elements.append(self.pm_invisible_shape)

        # If texture is provided, use it
        self._texture: Texture

        # if texture already set, use it and rescale it!
        if texture:
            texture = self._texture_from_args(texture)
            texture.size = (self._size[0] + invisible_range, self._size[1] + invisible_range)
            self._texture = texture
            self._texture_surface = self._texture.generate()

        # If texture already generated by visible shape
        elif hasattr(self, 'texture'):
            mask_radius = self._radius + 1 + invisible_range
            mask_size = (int(2 * mask_radius),) * 2
            self._texture_surface = pygame.transform.scale(self._texture_surface,
                                                           mask_size)

        # If no texture is set, default is grey
        else:
            texture = ColorTexture((100, 100, 100))
            texture.size = (self._size[0] + invisible_range, self._size[1] + invisible_range)
            self._texture = texture
            self._texture_surface = self._texture.generate()

    def create_pm_shape(self, additional_range: Optional[float] = None):

        pm_shape = super().create_pm_shape(additional_range=additional_range)
        pm_shape.sensor = True

        return pm_shape

    @abstractmethod
    def _set_pm_collision_type(self, pm_shape):
        ...
