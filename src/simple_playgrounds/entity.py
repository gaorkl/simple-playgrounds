""" Contains the base class for entities.

Entity classes should be used to create body parts of
an agent, scene entities, spawners, timers, etc.

Entity is the generic building block of physical and interactive
objects in simple-playgrounds.

"""
from __future__ import annotations
import math
from abc import ABC, abstractmethod
from typing import Union, Tuple, Dict, List, Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from simple_playgrounds.playground.playground import Playground
    from simple_playgrounds.agent.actuators import Grasp

import pygame
import pymunk
from simple_playgrounds.common.definitions import FRICTION_ENTITY, ELASTICITY_ENTITY, MAX_ATTEMPTS_OVERLAPPING, \
    PymunkCollisionCategories, VISIBLE_ALPHA, INVISIBLE_ALPHA

from simple_playgrounds.common.position_utils import CoordinateSampler, Trajectory, InitCoord, Coordinate
from simple_playgrounds.common.texture import Texture, TextureGenerator, ColorTexture

from simple_playgrounds.common.contour import get_contour, GeometricShapes, get_vertices

# pylint: disable=line-too-long
# pylint: disable=too-many-instance-attributes


class Entity(ABC):
    """
    Base class that defines the interface between playground and entities that are composing it.
    Entities can be: SceneElement, Agent, Spawner, Timer, ...
    """

    index_entity = 0

    def __init__(self,
                 name: Optional[str] = None):

        self._name: str

        if not name:
            name = self.__class__.__name__ + '_' + str(Entity.index_entity)
        self._name = name

        Entity.index_entity += 1

        self._playground: Optional[Playground] = None

    @property
    def playground(self):
        return self._playground

    def add_to_playground(self, playground: Playground):
        if self._playground:
            raise ValueError('Entity {} already in a Playground'.format(self._name))

        self._playground = playground
        self._add_to_playground()

    @abstractmethod
    def _add_to_playground(self):
        """
        Add pymunk elements to playground space.
        Add entity to lists or dicts in playground.
        """
        ...

    def remove_from_playground(self):
        self._remove_from_playground()

    @abstractmethod
    def _remove_from_playground(self):
        """
        Remove pymunk elements from playground space.
        Remove entity from lists or dicts in playground.
        """

    @abstractmethod
    def pre_step(self):
        """
        Computes all the necessary calculations before the pymunk engine steps.
        """
        ...

    @abstractmethod
    def update(self):
        """
        Updates the entity state after pymunk engine steps.
        """
        ...

    @abstractmethod
    def reset(self):
        """
        Upon reset of the environment, revert the entity back to its original state.
        """
        ...

    @property
    def name(self):
        return self._name


class PlaygroundEntity(Entity, ABC):

    """
    Playground Entities are entities that are present in the playground.
    They have a texture that defines their appearance for user and for sensors.
    """

    def __init__(self,
                 texture: Union[Texture, Dict, Tuple[int, int, int]],
                 temporary: Optional[bool] = False,
                 **kwargs,
                 ):

        super().__init__(**kwargs)

        self._contour = get_contour(**kwargs)
        self.pm_body: Optional[pymunk.Body] = self._set_pm_body()
        self._pm_shapes: List[pymunk.Shape] = []

        self._temporary = temporary
        self._produced_by: Optional[Entity] = None

        if isinstance(texture, Dict):
            texture = TextureGenerator.create(**texture)

        elif isinstance(texture, (tuple, list)):
            texture = ColorTexture(color=texture)

        assert isinstance(texture, Texture)

        texture.size = self._contour.size

        self._texture: Texture = texture
        self._texture_surface = self._texture.generate()

    def _create_mask(self, alpha):

        # pylint: disable-all

        mask_radius = self._contour.radius + 1

        center = (mask_radius,) * 2
        mask_size = (int(2 * mask_radius),) * 2
        mask = pygame.Surface(mask_size, pygame.SRCALPHA)
        mask.fill((0, 0, 0, 0))

        if self._contour.shape == GeometricShapes.CIRCLE:
            pygame.draw.circle(mask, (255, 255, 255, alpha), center,
                               mask_radius)

        else:
            vert = get_vertices(self._contour, offset_angle=self.angle)
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


    @property
    def produced_by(self):
        return self._produced_by

    @produced_by.setter
    def produced_by(self, producer: Entity):
        self._produced_by = producer
        self._temporary = True

    @property
    def temporary(self):
        return self._temporary

    @abstractmethod
    def _set_pm_body(self):
        """ Shapes must be attached to a body."""
        ...

    def _create_pm_shape(self):

        if self._contour.shape == GeometricShapes.CIRCLE:
            pm_shape = pymunk.Circle(self.pm_body, self._contour.radius)

        else:
            pm_shape = pymunk.Poly(self.pm_body, self._contour.vertices)

        pm_shape.friction = FRICTION_ENTITY
        pm_shape.elasticity = ELASTICITY_ENTITY

        return pm_shape

    @property
    def contour(self):
        return self._contour

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
        return self.pm_body.angle % (2 * math.pi)

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


class PhysicalEntity(PlaygroundEntity, ABC):
    """
    PhysicalEntity creates a physical object that can collide with other Physical Entities.
    It deals with physical properties such as the mass, visual texture, whether it is transparent or traversable.
    PhysicalEntity is visible and non-traversable by default.
    An agent is composed of multiple PhysicalEntity that are attached to each other.
    """

    def __init__(
            self,
            movable: bool = False,
            mass: Optional[float] = None,
            traversable: bool = False,
            transparent: bool = False,
            **kwargs,
    ):

        super().__init__(**kwargs)

        if movable:
            assert mass
        self._movable = movable

        self._mass = mass

        self._pm_shape = self._create_pm_shape()

        # By default, a physical entity collides with all
        if transparent and traversable:
            raise ValueError('Physical Object can not be transparent and traversable')

        # If traversable, collides only with sensors
        if traversable:
            self._pm_shape.filter = pymunk.ShapeFilter(categories=2 ** PymunkCollisionCategories.TRAVERSABLE.value,
                                                       mask=2 ** PymunkCollisionCategories.SENSOR.value |
                                                      2 ** PymunkCollisionCategories.SENSOR_CONTACT.value)
        self._traversable = traversable

        # If transparent, collides with everything. Sensors don't collide except for contact sensor.
        if transparent:
            self._pm_shape.filter = pymunk.ShapeFilter(categories=2 ** PymunkCollisionCategories.TRANSPARENT.value,
                                                       mask=pymunk.ShapeFilter.ALL_MASKS() ^
                                                      (2 ** PymunkCollisionCategories.SENSOR.value))
        self._transparent = transparent

        self._pm_shapes = [self._pm_shape]

        # To be set when entity is added to playground.
        self._initial_coordinates: Optional[InitCoord] = None
        self._trajectory: Optional[Trajectory] = None

        # Used to set an element which is not supposed to overlap
        self._allow_overlapping = False
        self._overlapping_strategy_set = False
        self._max_attempts = MAX_ATTEMPTS_OVERLAPPING

        self._movable = movable

        self._held_by: List[Grasp] = []

    @property
    def held_by(self):
        return self._held_by

    @held_by.setter
    def held_by(self, grasper: Grasp):
        self._held_by.append(grasper)

    def released_by(self, grasper):
        assert grasper in self._held_by
        self._held_by.remove(grasper)

    def get_pixel(self, relative_pos):
        return self._texture.get_pixel(relative_pos)

    @property
    def base_color(self):
        return self._texture.base_color

    # BODY AND SHAPE
    def _set_pm_body(self):

        if not self._movable:
            return pymunk.Body(body_type=pymunk.Body.STATIC)

        assert isinstance(self._mass, (float, int))

        if self._contour.shape == GeometricShapes.CIRCLE:
            moment = pymunk.moment_for_circle(self._mass, 0,
                                              self._contour.radius)

        else:
            moment = pymunk.moment_for_poly(self._mass, self._contour.vertices)

        return pymunk.Body(self._mass, moment)

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

    # INTERFACE

    def pre_step(self):
        """
        Performs calculation before the physical environment steps.
        """

        if self._trajectory:
            self.position, self.angle = next(self._trajectory)

    def reset(self):
        """
        Reset the trajectory and initial position
        """

        if self._trajectory:
            self._trajectory.reset()

        self.velocity = (0, 0)
        self.angular_velocity = 0

        self.position, self.angle = self.initial_coordinates

    def draw(self, surface, viewpoint, draw_transparent=False):

        if self._transparent and not draw_transparent:
            return

        if self._transparent:
            mask = self._create_mask(alpha=INVISIBLE_ALPHA)
        else:
            mask = self._create_mask(alpha=VISIBLE_ALPHA)

        mask_rect = mask.get_rect()
        mask_rect.center = self.position - viewpoint
        surface.blit(mask, mask_rect, None)


class InteractiveEntity(PlaygroundEntity, ABC):

    def __init__(self, **kwargs):

        super().__init__(**kwargs)

        self._pm_interactive_shape = self._create_pm_shape()
        self._pm_interactive_shape.sensor = True

        self._set_pm_collision_handler()

    @abstractmethod
    def _set_pm_collision_handler(self):
        """
        Set the collision handler for the interactive shape.
        """
        ...

    def draw(self, surface, viewpoint, draw_transparent=False):

        if not draw_transparent:
            return

        mask = self._create_mask(alpha=INVISIBLE_ALPHA)
        mask_rect = mask.get_rect()
        mask_rect.center = self.position - viewpoint
        surface.blit(mask, mask_rect, None)


class StandAloneInteractive(InteractiveEntity, ABC):

    def _set_pm_body(self):
        return pymunk.Body(body_type=pymunk.Body.STATIC)


class AnchoredInteractive(InteractiveEntity, ABC):

    def __init__(self, anchor: PhysicalEntity, **kwargs):

        self._anchor = anchor
        super().__init__(**kwargs)

    def _set_pm_body(self):
        return self._anchor.pm_body
