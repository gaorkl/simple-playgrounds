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

import pygame
import pymunk
from simple_playgrounds.common.definitions import FRICTION_ENTITY, ELASTICITY_ENTITY, MAX_ATTEMPTS_OVERLAPPING

from simple_playgrounds.common.position_utils import CoordinateSampler, Trajectory, InitCoord, Coordinate
from simple_playgrounds.common.texture import Texture, TextureGenerator, ColorTexture

from simple_playgrounds.common.contour import get_contour, GeometricShapes, get_vertices


# pylint: disable=line-too-long
# pylint: disable=too-many-instance-attributes


class Entity(ABC):
    """
    Base class that defines the interface between playground and entities that are composing it.
    Entities can be: SceneElement, Agent, Spawner, Timer, ...
    Entity can be in multiple teams.
    """

    index_entity = 0

    def __init__(self,
                 name: Optional[str] = None,
                 **kwargs):

        self._name: str
        if not name:
            name = self.__class__.__name__ + '_' + str(Entity.index_entity)
        self._name = name

        self._playground: Optional[Playground] = None
        self._teams: List[str] = []

        Entity.index_entity += 1

    @property
    def playground(self):
        return self._playground

    @property
    def name(self):
        return self._name

    def add_to_playground(self, playground: Playground, **kwargs):
        if self._playground:
            raise ValueError('Entity {} already in a Playground'.format(self._name))

        self._playground = playground

        # If in a team when added to the playground, add the team.
        for team in self._teams:
            if team not in self._playground.teams:
                self._playground.add_team(team)

        self._playground.update_teams()

        # One new filters have been resolved, add to playground
        self._add_to_playground(**kwargs)

    @abstractmethod
    def _add_to_playground(self, **kwargs):
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

    def add_to_team(self, team):
        self._teams.append(team)

        # If already in playground, add the team
        if self._playground:

            if team not in self._playground.teams.keys():
                self._playground.add_team(team)

            self._playground.update_teams()

    def update_team_filter(self):
        pass

    @abstractmethod
    def pre_step(self):
        """
        Preliminary calculations before the pymunk engine steps.
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


class EmbodiedEntity(Entity, ABC):

    """
    Embodied Entities are entities that are present in the playground.
    They have:
     - a physical body
     - possibly multiple shapes

    They occupy space, have an appearance.
    They also have a position, angle, velocity.
    Their appearance can be used for user display and for sensors.

    """

    def __init__(self,
                 texture: Union[Texture, Dict, Tuple[int, int, int]],
                 temporary: Optional[bool] = False,
                 **kwargs,
                 ):

        super().__init__(**kwargs)

        self._contour = get_contour(**kwargs)
        self._pm_body: Optional[pymunk.Body] = self._set_pm_body()
        self._pm_shape: pymunk.Shape = self._set_pm_shape()

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

        # To be set when entity is added to playground.
        self._initial_coordinates: Optional[InitCoord] = None
        self._trajectory: Optional[Trajectory] = None
        self._initial_coordinate_sampler = None
        self._allow_overlapping = True

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

    @property
    def contour(self):
        return self._contour

    @property
    def coordinates(self):
        """
        Tuple ( (x,y), angle ).
        """
        return self.position, self.angle

    @property
    def position(self):
        """ Position (x, y) """
        return self._pm_body.position

    @property
    def angle(self):
        """ Absolute orientation """
        return self._pm_body.angle % (2 * math.pi)

    @property
    def velocity(self):
        return self._pm_body.velocity

    @property
    def angular_velocity(self):
        return self._pm_body.angular_velocity

    @property
    def base_color(self):
        return self._texture.base_color

    def _create_pm_shape(self):

        if self._contour.shape == GeometricShapes.CIRCLE:
            pm_shape = pymunk.Circle(self._pm_body, self._contour.radius)

        else:
            pm_shape = pymunk.Poly(self._pm_body, self._contour.vertices)

        pm_shape.friction = FRICTION_ENTITY
        pm_shape.elasticity = ELASTICITY_ENTITY

        return pm_shape

    @abstractmethod
    def _set_pm_shape(self):
        """ Shape must be set. Interactive or Not. """
        ...

    @abstractmethod
    def _set_pm_body(self):
        """ Shapes must be attached to a body."""
        ...

    def move_to(self,
                coordinates: Coordinate,
                velocity: Optional[Coordinate] = None,
                allow_overlapping: bool = True,
                ):

        if not allow_overlapping:
            assert not self._overlaps(coordinates)

        self._pm_body.position, self._pm_body.angle = coordinates

        if velocity:
            self._pm_body.velocity, self._pm_body.angular_velocity = velocity

        if self._pm_body.space:
            self._pm_body.space.reindex_shapes_for_body(self._pm_body)

    def _set_initial_coordinates(self,
                                 initial_coordinates: Union[Coordinate, CoordinateSampler, Trajectory],
                                 allow_overlapping: bool = True,
                                 ):

        if isinstance(initial_coordinates, Trajectory):
            self._trajectory = initial_coordinates

        elif isinstance(initial_coordinates, CoordinateSampler):
            self._initial_coordinate_sampler = initial_coordinates

        else:
            if not isinstance(initial_coordinates, CoordinateSampler):
                assert len(initial_coordinates) == 2 and len(
                    initial_coordinates[0]) == 2
            self._initial_coordinates = initial_coordinates

        self._allow_overlapping = allow_overlapping

    def _move_to_initial_position(self):
        """
        Initial coordinates of the Entity.
        Can be tuple of (x,y), angle, or PositionAreaSampler object
        """

        vel = ((0, 0), 0)
        if self._initial_coordinates:
            coordinates = self._initial_coordinates

        elif self._initial_coordinate_sampler:
            coordinates = self._sample_valid_location(self._initial_coordinate_sampler)

        elif self._trajectory:
            self._trajectory.reset()
            coordinates = next(self._trajectory)

        else:
            raise ValueError('Initial Coordinate is not set')

        assert self._playground.within_playground(coordinates)

        if not self._allow_overlapping and self._overlaps(coordinates):
            raise ValueError('Entity could not be placed without overlapping')

        self.move_to(coordinates, vel)

    def _overlaps(self, coordinates):
        """ Tests whether new coordinate would lead to physical collision """

        dummy_body = pymunk.Body(body_type=pymunk.Body.STATIC)
        dummy_shape = self._create_pm_shape()
        dummy_shape.body = dummy_body
        dummy_shape.sensor = True

        self._playground.space.add(dummy_shape.body, dummy_shape)

        dummy_shape.body.position, dummy_shape.body.angle = coordinates
        self._playground.space.reindex_static()

        overlaps = self._playground.space.shape_query(dummy_shape)
        self._playground.space.remove(dummy_shape.body, dummy_shape)

        # remove sensor shapes
        overlaps = [elem for elem in overlaps if not elem.shape.sensor and elem.shape is not self._pm_shape]

        self._playground.space.reindex_static()

        return bool(overlaps)

    def _sample_valid_location(self, sampler: CoordinateSampler):

        attempt = 0
        coordinates = sampler.sample()

        # create temporary shape to check for collision
        while self._overlaps(coordinates) and (attempt <= MAX_ATTEMPTS_OVERLAPPING):
            coordinates = sampler.sample()
            attempt += 1

        if not self._overlaps(coordinates):
            return coordinates

        raise ValueError('Entity could not be placed without overlapping')

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

    def get_pixel(self, relative_pos):
        return self._texture.get_pixel(relative_pos)



