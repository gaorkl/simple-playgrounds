from __future__ import annotations


from abc import ABC
from typing import Optional

import pymunk

from PIL import Image

from simple_playgrounds.entity import Entity

import math
from abc import ABC, abstractmethod
from typing import Optional, TYPE_CHECKING
from arcade import Texture, Sprite


if TYPE_CHECKING:
    from simple_playgrounds.playground.playground import Playground

from simple_playgrounds.common.definitions import FRICTION_ENTITY, ELASTICITY_ENTITY

from simple_playgrounds.common.position_utils import CoordinateSampler, InitCoord, Coordinate


class EmbodiedEntity(Entity, ABC):

    """
    Embodied Entities are elementary entities physically present in the playground.
    They can interact with other Embodied Entities through
    pymunk collisions.

    """

    def __init__(self,
                 playground: Playground,
                 initial_coordinates: InitCoord,
                 filename: Optional[str] = None,
                 texture: Optional[Texture] = None,
                 scale: float = 1,
                 mass: Optional[float] = None,
                 temporary: bool = False,
                 allow_overlapping: bool = True,
                 **kwargs,
                 ):

        super().__init__(playground, **kwargs)
        
        # Shape, body and appearance
        self._base_sprite = self._get_base_sprite(filename, texture, scale)
        self._mass = mass

        self._pm_body: pymunk.Body = self._get_pm_body()
        self._pm_shape: pymunk.Shape = self._get_pm_shape()
        self._add_to_pymunk_space()

        # Initial Positioning of the entities.
        self._allow_overlapping = allow_overlapping
        self._initial_coordinates = initial_coordinates
        self._moved = False
        self._move_to_initial_coordinates()

        # Interactions and collisions
        self._set_pm_collision_type()
        self.update_team_filter()

        # Flags 
        self._temporary = temporary
        self._produced_by: Optional[Entity] = None


    #############
    # Properties
    #############

    @property
    def pm_shape(self):
        return self._pm_shape

    @property
    def pm_body(self):
        return self._pm_body

    @property
    def produced_by(self):
        return self._produced_by

    @property
    def temporary(self):
        return self._temporary

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
    def color_uid(self):
        return self._uid&255, (self._uid>>8)&255, (self._uid>>16)&255, 255


    ##############
    # Sprites
    ##############

    def _get_base_sprite(self, texture, filename, scale):
        
        if not (bool(filename) ^ bool(texture)):
            raise ValueError("Either filename or texture should be specified")

        return Sprite(texture=texture, filename=filename,
                      scale=scale, hit_box_algorithm='Detailed', hit_box_detail=0.1)

    def _get_sprite(self, zoom: float = 1) -> Sprite:

        texture = self._base_sprite.texture
        assert isinstance(texture, Texture)

        base_scale = self._base_sprite.scale

        return Sprite(texture=texture, scale=zoom*base_scale,
                      hit_box_algorithm='Detailed', hit_box_detail=0.1)

    def _get_id_sprite(self, zoom: float = 1) -> Sprite:
        
        base_texture = self._base_sprite.texture
        assert isinstance(base_texture, Texture)

        img_uid = Image.new('RGBA', base_texture.size)
        pixels = img_uid.load()
        pixels_texture = base_texture.image.load()

        for i in range(img_uid.size[0]):
            for j in range(img_uid.size[1]):

                if pixels_texture[i, j] != (0, 0, 0, 0): #type: ignore
                    pixels[i, j] = self.color_uid #type: ignore
            
        texture = Texture(name=str(self._uid), image=img_uid,
                          hit_box_algorithm='Detailed', hit_box_detail=0.1)

        base_scale = self._base_sprite.scale

        return Sprite(texture=texture, scale=zoom*base_scale,
                      hit_box_algorithm='Detailed', hit_box_detail=0.1)

    ###################
    # Pymunk objects
    ###################

    @abstractmethod
    def _get_pm_body(self) -> pymunk.Body:
        """
        Set pymunk body. Shapes are attached to a body.
        """
        ...

    def _get_pm_shape(self):

        base_sprite = self._base_sprite
        scale = base_sprite.scale

        vertices = [(x*scale, y*scale) for x,y in base_sprite.get_hit_box()]
        pm_shape = pymunk.Poly(body = self._pm_body, vertices=vertices)
        
        pm_shape.friction = FRICTION_ENTITY
        pm_shape.elasticity = ELASTICITY_ENTITY

        return pm_shape


    def _add_to_pymunk_space(self):
        self._playground.space.add(self._pm_body, self._pm_shape)

    def _remove_from_pymunk_space(self):
        self._playground.space.remove(self._pm_body, self._pm_shape)


    ##############
    # COLLISIONS AND TEAMS
    ##############

    @abstractmethod
    def _set_pm_collision_type(self):
        """
        Set the collision handler for the shape.
        """
        ...
    
    def update_team_filter(self):
        
        categ = self._pm_shape.filter.categories

        for team in self._teams:
            categ = categ | 2 ** self._playground.teams[team]

        mask = self._pm_shape.filter.mask
        for team in self._playground.teams:

            if team not in self._teams:
                mask = mask | 2 ** self._playground.teams[team] ^ 2 ** self._playground.teams[team]

        self._pm_shape.filter = pymunk.ShapeFilter(categories=categ, mask=mask)
    
    ###################
    # Position and Move
    ###################

    def move_to(self,
                coordinates: Coordinate,
                allow_overlapping: bool = True,
                keep_velocity: bool = False):

        if (not allow_overlapping) and self._playground.overlaps(self, coordinates):
            raise ValueError("Entity overlaps but should not")

        if self._playground.within_playground(coordinates):
            raise ValueError("Entity is not placed within Playground boundaries")

        position, angle = coordinates

        # Calculate Velocities
        if keep_velocity:
            relative_velocity = self._pm_body.velocity.rotated(-self._pm_body.angle)
            absolute_velocity = relative_velocity.rotated(angle)
            angular_velocity = self._pm_body.angular_velocity
        else:
            absolute_velocity, angular_velocity = (0, 0), 0

        # Apply new position and velocities
        self._pm_body.position, self._pm_body.angle = position, angle
        self._pm_body.velocity = absolute_velocity
        self._pm_body.angular_velocity = angular_velocity

        if self._pm_body.space:
            self._pm_body.space.reindex_shapes_for_body(self._pm_body)

        self._moved = True

    def _move_to_initial_coordinates(self):
        """
        Initial coordinates of the Entity.
        Can be tuple of (x,y), angle, or PositionAreaSampler object
        """

        if isinstance(self._initial_coordinates, (tuple, list)):
            coordinates = self._initial_coordinates

        elif isinstance(self._initial_coordinates, CoordinateSampler):
            coordinates = self._sample_valid_coordinate()

        else:
            raise ValueError('Initial Coordinate is not set')

        self.move_to(coordinates, keep_velocity=False)
    
    def _sample_valid_coordinate(self) -> Coordinate:

        sampler = self._initial_coordinates
        assert isinstance(sampler, CoordinateSampler)

        for coordinate in sampler.sample():
            if not self._playground.overlaps(self, coordinate):
                return coordinate

        raise ValueError('Entity could not be placed without overlapping')

    ##############
    # PLayground Interactions
    ################

    def pre_step(self):

        self._moved = False

    def remove(self, definitive: bool = False):
        
        self._remove_from_pymunk_space()
        super().remove(definitive=definitive or self._temporary)
        
    def reset(self):

        # Remove completely if temporary
        if self._temporary:
            self.remove()
            return

        if self._removed:
            self._add_to_pymunk_space()
        self._move_to_initial_coordinates()
        self._removed = False
