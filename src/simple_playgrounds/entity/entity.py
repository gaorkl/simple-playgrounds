""" Contains the base class for entities.

Entity classes should be used to create body parts of
an agent, scene entities, spawners, timers, etc.

Entity is the generic building block of physical and interactive
objects in simple-playgrounds.

"""
from __future__ import annotations
import math
from abc import ABC, abstractmethod
from typing import Dict, Union, List, Optional, TYPE_CHECKING

import numpy as np

if TYPE_CHECKING:
    from simple_playgrounds.playground.playground import Playground
    from simple_playgrounds.common.view import View

import pymunk
import matplotlib.patches as mpatches



from simple_playgrounds.common.definitions import FRICTION_ENTITY, ELASTICITY_ENTITY

from simple_playgrounds.common.position_utils import CoordinateSampler, Trajectory, InitCoord, Coordinate
from simple_playgrounds.common.appearance.appearance import Appearance

from simple_playgrounds.common.contour import Contour, GeometricShapes
from simple_playgrounds.common.view import FixedGlobalView, AnchoredView


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
        self._add_pm_elements(**kwargs)

    @abstractmethod
    def _add_pm_elements(self, **kwargs):
        """
        Add pymunk elements to playground space.
        Add entity to lists or dicts in playground.
        """
        ...

    def remove_from_playground(self):
        self._remove_pm_elements()
        self._playground = None

    @abstractmethod
    def _remove_pm_elements(self):
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
     - a shape that can be visible/invisible traversable/solid

    They occupy space, have an appearance.
    They also have a position, angle, velocity.
    Their appearance can be used for user display and for sensors.

    """

    def __init__(self,
                 appearance: Appearance,
                 temporary: Optional[bool] = False,
                 contour: Optional[Contour] = None,
                 **kwargs,
                 ):

        super().__init__(**kwargs)

        if contour:
            self._contour = contour
        else:
            self._contour = Contour(**kwargs)

        self._pm_body: pymunk.Body = self._set_pm_body()
        self._pm_shape: pymunk.Shape = self._set_pm_shape()

        self._temporary = temporary
        self._produced_by: Optional[Entity] = None

        self._appearance = appearance
        self._appearance.contour = self._contour

        # To be set when entity is added to playground.
        self._initial_coordinates: Optional[InitCoord] = None
        self._trajectory: Optional[Trajectory] = None
        self._initial_coordinate_sampler: Optional[CoordinateSampler] = None
        self._allow_overlapping = True

        # artists for matplotlib rendering
        self._artists: Dict[View, mpatches.Patch] = {}

    @property
    def pm_shape(self):
        return self._pm_shape

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
        return not isinstance(self._pm_body, pymunk.Body.STATIC) and not self._trajectory

    @property
    def contour(self):
        return self._contour

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
            pm_shape = pymunk.Circle(self._pm_body, self._contour.radius)

        else:
            pm_shape = pymunk.Poly(self._pm_body, self._contour.vertices)

        pm_shape.friction = FRICTION_ENTITY
        pm_shape.elasticity = ELASTICITY_ENTITY

        return pm_shape

    def update_view(self, view: View):

        if view not in self._artists:
            self._create_artist(view)

        artist = self._artists[view]

        # if entity disappear, remove it
        if not self._playground:
            self._artists.pop(view)
            artist.remove()
            return

        if isinstance(view, FixedGlobalView) and not self.movable:
            return

        self._update_artist_position(view)
        self._update_artist_appearance(view)

        view.canvas.figure.draw_artist(artist)

    def _create_artist(self, view):

        if self._contour.shape == GeometricShapes.CIRCLE:
            artist = mpatches.Circle((0, 0), self._contour.radius * view.zoom, fill=True)

        elif self._contour.shape == GeometricShapes.POLYGON:
            vertices = np.asarray(self._contour.vertices) * view.zoom
            artist = mpatches.Polygon(xy=vertices, fill=True)

        else:
            artist = mpatches.RegularPolygon((0, 0),
                                           radius=self._contour.radius * view.zoom,
                                           numVertices=self._contour.shape.value,
                                           fill=True)
        artist.set_animated(True)
        artist.set_antialiased(False)
        self._artists[view] = artist
        view.add_patch(artist)

    def _update_artist_position(self, view):

        relative_position = (self.position - view.position).rotated(-view.angle)
        relative_position *= view.zoom

        if self._contour.shape == GeometricShapes.POLYGON:

            vertices = self._contour.get_rotated_vertices(self.angle - view.angle)
            vertices = np.asarray(vertices)*view.zoom + relative_position
            self._artists[view].set(xy=vertices)

        elif self._contour.shape == GeometricShapes.CIRCLE:

            self._artists[view].set(center=relative_position)

        else:
            self._artists[view].xy = relative_position
            self._artists[view].orientation = self.angle - view.angle

    def _update_artist_appearance(self, view):
        # Should be modified to apply images, textures, ony when asked.
        self._artists[view].set(color=(0.2, 0.1, 0.3))

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

    def _set_initial_coordinates(self,
                                 initial_coordinates: Optional[Union[Coordinate,
                                                                     CoordinateSampler,
                                                                     Trajectory]] = None,
                                 allow_overlapping: bool = True,
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
            self._initial_coordinate_sampler.rng = self._playground.rng

        else:
            assert len(initial_coordinates) == 2 and len(
                    initial_coordinates[0]) == 2
            self._initial_coordinates = initial_coordinates

        self._allow_overlapping = allow_overlapping
        self._initial_coordinates_set = True

    def _move_to_initial_coordinates(self):
        """
        Initial coordinates of the Entity.
        Can be tuple of (x,y), angle, or PositionAreaSampler object
        """

        vel = ((0, 0), 0)
        if self._initial_coordinates:
            coordinates = self._initial_coordinates

        elif self._initial_coordinate_sampler:
            coordinates = self._sample_valid_coordinate(self._initial_coordinate_sampler)

        elif self._trajectory:
            self._trajectory.reset()
            coordinates = next(self._trajectory)

        else:
            raise ValueError('Initial Coordinate is not set')

        assert self._playground.within_playground(coordinates)

        if not self._allow_overlapping and self._overlaps(coordinates):
            raise ValueError('Entity could not be placed without overlapping')

        self.move_to(coordinates, vel, initial_positioning=True)

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

    def _sample_valid_coordinate(self, sampler: CoordinateSampler):

        for coordinate in sampler.sample():
            if not self._overlaps(coordinate):
                return coordinate

        raise ValueError('Entity could not be placed without overlapping')

    def get_pixel(self, relative_pos):
        return self._appearance.get_pixel(relative_pos)
