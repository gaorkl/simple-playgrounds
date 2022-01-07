from __future__ import annotations
from abc import ABC
from typing import Optional

import pymunk

from simple_playgrounds.entity import Entity
from simple_playgrounds.entity.embodied.appearance.appearance import Appearance
from simple_playgrounds.entity.embodied.contour import Contour

import math
from abc import ABC, abstractmethod
from typing import Dict, Union, List, Optional, TYPE_CHECKING

import numpy as np

if TYPE_CHECKING:
    from simple_playgrounds.playground.playground import Playground
    from simple_playgrounds.common.view import View

import pymunk


from simple_playgrounds.common.definitions import FRICTION_ENTITY, ELASTICITY_ENTITY

from simple_playgrounds.common.position_utils import CoordinateSampler, Trajectory, InitCoord, Coordinate

from simple_playgrounds.entity.embodied.contour import GeometricShapes
from simple_playgrounds.entity.embodied.patch import Patch


class EmbodiedEntity(Entity, ABC):

    """
    Embodied Entities are elementary entities that present in the playground.
    They can interact with other Embodied Entities through
    pymunk collisions.

    """

    def __init__(self,
                 appearance: Appearance,
                 contour: Optional[Contour] = None,
                 temporary: Optional[bool] = False,
                 **kwargs,
                 ):

        if contour:
            self._contour = contour
        else:
            self._contour = Contour(**kwargs)

        self._pm_body: pymunk.Body = self._set_pm_body()
        self._pm_shape: pymunk.Shape = self._set_pm_shape()

        super().__init__(**kwargs)
        
        self._add_to_pymunk_space()

        self._temporary = temporary
        self._produced_by: Optional[Entity] = None

        self._appearance = appearance
        self._appearance.contour = self._contour

        # To be set when entity is added to playground.
        self._initial_coordinates: Optional[InitCoord] = None
        self._trajectory: Optional[Trajectory] = None
        self._initial_coordinate_sampler: Optional[CoordinateSampler] = None
        self._allow_overlapping = True

        self._set_initial_coordinates(**kwargs)
        self._move_to_initial_coordinates()

        # Patch to display the entity in TopDown view
        self._patches: Dict[View, Patch] = {}

        self._set_pm_collision_type()

    @abstractmethod
    def _set_pm_collision_type(self):
        """
        Set the collision handler for the interactive shape.
        """
        ...

    @property
    def pm_shape(self):
        return self._pm_shape

    @property
    def pm_body(self):
        return self._pm_body

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
    def movable(self):
        return (not self._pm_body.body_type == pymunk.Body.STATIC 
                and not self._trajectory)

    @property
    def contour(self):
        return self._contour

    @property
    def appearance(self):
        return self._appearance

    @property
    def coordinates(self):
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
        return self._appearance.base_color

    def _create_pm_shape(self):

        if self._contour.shape == GeometricShapes.CIRCLE:
            assert self._contour.radius
            pm_shape = pymunk.Circle(self._pm_body, self._contour.radius)

        else:
            assert self._contour.vertices
            pm_shape = pymunk.Poly(self._pm_body, self._contour.vertices)

        pm_shape.friction = FRICTION_ENTITY
        pm_shape.elasticity = ELASTICITY_ENTITY

        return pm_shape

    def _add_to_pymunk_space(self, **_):
        self._playground.space.add(self._pm_body, self._pm_shape)



    def remove_from_playground(self):
        self._playground.space.remove(self._pm_body, self._pm_shape)

    def update_view(self, view: View, **kwargs):

        if view not in self._patches:
            patch = Patch(entity=self, view=view, **kwargs)
            self._patches[view] = patch

        patch = self._patches[view]

        # if entity disappear, remove it
        if not self._playground:
            self._patches.pop(view)
            patch.remove_patch()
            return

        patch.update()

    @abstractmethod
    def _set_pm_shape(self) -> pymunk.Shape:
        """ Shape must be set. Interactive or Not. """
        ...

    @abstractmethod
    def _set_pm_body(self) -> pymunk.Body:
        """ Shapes must be attached to a body."""
        ...

    def move_to(self,
                coordinates: Coordinate,
                velocity: Optional[Coordinate] = None,
                allow_overlapping: bool = True,
                initial_positioning: bool = False,
                ):

        if not initial_positioning and not self.movable:
            raise ValueError('Trying to move something that is not movable!')

        if not allow_overlapping:
            assert not self._overlaps(coordinates)

        self._pm_body.position, self._pm_body.angle = coordinates

        if velocity:
            self._pm_body.velocity, self._pm_body.angular_velocity = velocity

        if self._pm_body.space:
            self._pm_body.space.reindex_shapes_for_body(self._pm_body)

    def _set_initial_coordinates(
        self,
        initial_coordinates: Optional[
            Union[Coordinate, CoordinateSampler, Trajectory]] = None,
        allow_overlapping: bool = True,
        **_,
    ):

        # if no initial coordinate is provided but they are already set
        if not initial_coordinates and (self._trajectory
                                        or self._initial_coordinates
                                        or self._initial_coordinate_sampler):
            return

        if isinstance(initial_coordinates, Trajectory):
            self._trajectory = initial_coordinates

        elif isinstance(initial_coordinates, CoordinateSampler):
            self._initial_coordinate_sampler = initial_coordinates
            assert self._playground
            self._initial_coordinate_sampler.rng = self._playground.rng

        else:
            assert initial_coordinates
            assert len(initial_coordinates) == 2 and len(
                    initial_coordinates[0]) == 2
            self._initial_coordinates = initial_coordinates

        self._allow_overlapping = allow_overlapping

    def _move_to_initial_coordinates(self):
        """
        Initial coordinates of the Entity.
        Can be tuple of (x,y), angle, or PositionAreaSampler object
        """

        vel = ((0, 0), 0)
        if self._initial_coordinates:
            coordinates = self._initial_coordinates

        elif self._initial_coordinate_sampler:
            coordinates = self._sample_valid_coordinate(
                self._initial_coordinate_sampler)

        elif self._trajectory:
            self._trajectory.reset()
            coordinates = next(self._trajectory)

        else:
            raise ValueError('Initial Coordinate is not set')

        assert (self._playground and
                self._playground.within_playground(coordinates))

        if not self._allow_overlapping and self._overlaps(coordinates):
            raise ValueError('Entity could not be placed without overlapping')
        
        self.move_to(coordinates, vel, initial_positioning=True)

    def _overlaps(self, coordinates):
        """ Tests whether new coordinate would lead to physical collision """

        dummy_body = pymunk.Body(body_type=pymunk.Body.STATIC)
        dummy_shape = self._create_pm_shape()
        dummy_shape.body = dummy_body
        dummy_shape.sensor = True
       
        assert self._playground
        self._playground.space.add(dummy_shape.body, dummy_shape)

        dummy_shape.body.position, dummy_shape.body.angle = coordinates
        self._playground.space.reindex_static()

        overlaps = self._playground.space.shape_query(dummy_shape)
        self._playground.space.remove(dummy_shape.body, dummy_shape)

        # remove sensor shapes
        overlaps = [elem for elem in overlaps 
                    if elem.shape and not elem.shape.sensor 
                    and elem.shape is not self._pm_shape]

        self._playground.space.reindex_static()

        return bool(overlaps)

    def _sample_valid_coordinate(self, 
                                 sampler: CoordinateSampler) -> Coordinate:

        for coordinate in sampler.sample():
            if not self._overlaps(coordinate):
                return coordinate

        raise ValueError('Entity could not be placed without overlapping')

    def get_pixel(self, **kwargs):
        return self._appearance.get_pixel(**kwargs)
