# pylint: disable=too-many-public-methods

from __future__ import annotations

import math
from abc import ABC, abstractmethod
from typing import List, Optional, Union

import pymunk
from arcade import Sprite, Texture
from PIL import Image

from ..utils.definitions import ELASTICITY_ENTITY, FRICTION_ENTITY
from ..utils.position import Coordinate, CoordinateSampler, InitCoord
from .entity import Entity

Teams = Union[str, List[str]]


class EmbodiedEntity(Entity, ABC):

    """
    Embodied Entities are elementary entities physically present in the playground.
    They can interact with other Embodied Entities through
    pymunk collisions.

    """

    def __init__(
        self,
        name: Optional[str] = None,
        filename: Optional[str] = None,
        texture: Optional[Texture] = None,
        radius: Optional[float] = None,
        width: Optional[float] = None,
        length: Optional[float] = None,
        temporary: bool = False,
        shape_approximation: Optional[str] = None,
        sprite_front_is_up: bool = False,
        teams: Optional[Teams] = None,
    ):

        super().__init__(name, teams, temporary)

        # Get the base sprite
        self._sprite_front_is_up = sprite_front_is_up
        self._base_sprite = Sprite(
            texture=texture,
            filename=filename,
            hit_box_algorithm="Detailed",
            hit_box_detail=1,
            flipped_diagonally=sprite_front_is_up,
            flipped_horizontally=sprite_front_is_up,
        )  # type: ignore

        # Get the scale and dimensions
        self._scale, self._radius, self._width, self._length = self._get_dimensions(
            radius, width, length
        )

        # Get pymunk elements
        self._pm_body = self._get_pm_body()
        self._pm_shapes = self._get_pm_shapes_from_sprite(shape_approximation)

        # Interactions and collisions
        self._set_pm_collision_type()

        # Flags
        self._moved = False

        # At the begining, not in playground
        self._allow_overlapping = False
        self._initial_coordinates: Optional[InitCoord] = None

    #############
    # Properties
    #############
    @property
    def pm_elements(self):
        return self._pm_shapes + [self._pm_body]

    @property
    def pm_shapes(self):
        return self._pm_shapes

    @property
    def pm_body(self):
        return self._pm_body

    @property
    def texture(self):
        return self._base_sprite.texture

    @property
    def radius(self):
        return self._radius

    @property
    def scale(self):
        return self._scale

    @property
    def width(self):
        return self._width

    @property
    def length(self):
        return self._length

    @property
    def coordinates(self):
        return self.position, self.angle

    @property
    def position(self):
        """Position (x, y)"""
        return self._pm_body.position

    @property
    def angle(self):
        """Absolute orientation"""
        return self._pm_body.angle % (2 * math.pi)

    @property
    def velocity(self):
        return self._pm_body.velocity

    @property
    def angular_velocity(self):
        return self._pm_body.angular_velocity

    @property
    def color_uid(self):
        return self._uid & 255, (self._uid >> 8) & 255, (self._uid >> 16) & 255, 255

    @property
    def moved(self):

        if self._moved:
            return True

        if self._pm_body.body_type == pymunk.Body.DYNAMIC:

            vel = self._pm_body.velocity.length
            if vel > 0.001:
                return True

            ang_vel = self._pm_body.angular_velocity
            if abs(ang_vel) > 0.001:
                return True

        return False

    @property
    def allow_overlapping(self):
        return self._allow_overlapping

    @allow_overlapping.setter
    def allow_overlapping(self, allow: bool):
        self._allow_overlapping = allow

    @property
    def initial_coordinates(self):
        return self._initial_coordinates

    @initial_coordinates.setter
    def initial_coordinates(self, init_coord: InitCoord):
        self._initial_coordinates = init_coord

    ##############
    # Init pm Elements
    ###############
    def _get_dimensions(self, radius, width, length):

        orig_radius = max(
            pymunk.Vec2d(*vert).length for vert in self._base_sprite.get_hit_box()
        )

        horiz = [pymunk.Vec2d(*vert).x for vert in self._base_sprite.get_hit_box()]
        vert = [pymunk.Vec2d(*vert).y for vert in self._base_sprite.get_hit_box()]

        orig_width = max(horiz) - min(horiz)
        orig_length = max(vert) - min(vert)

        # If radius imposed:
        if radius:
            scale = radius / orig_radius

        elif length:
            scale = length / orig_length

        elif width:
            scale = width / orig_width
        else:
            scale = 1

        width = scale * orig_width
        length = scale * orig_length
        radius = scale * orig_radius

        return scale, radius, width, length

    def _get_pm_shapes_from_sprite(self, shape_approximation):

        vertices = self._base_sprite.get_hit_box()

        vertices = [(x * self._scale, y * self._scale) for x, y in vertices]

        if shape_approximation == "circle":
            pm_shapes = [pymunk.Circle(self._pm_body, self._radius)]

        elif shape_approximation == "box":
            top = max(vert[0] for vert in vertices)
            bottom = min(vert[0] for vert in vertices)
            left = min(vert[1] for vert in vertices)
            right = max(vert[1] for vert in vertices)

            box_vertices = ((top, left), (top, right), (bottom, right), (bottom, left))

            pm_shapes = [pymunk.Poly(self._pm_body, box_vertices)]

        elif shape_approximation == "hull":
            pm_shapes = [pymunk.Poly(self._pm_body, vertices)]

        elif shape_approximation == "decomposition":

            if not pymunk.autogeometry.is_closed(vertices):
                vertices += [vertices[0]]

            if pymunk.area_for_poly(vertices) < 0:
                vertices = list(reversed(vertices))

            list_vertices = pymunk.autogeometry.convex_decomposition(
                vertices, tolerance=0.5
            )

            pm_shapes = []
            for vertices in list_vertices:
                pm_shape = pymunk.Poly(body=self._pm_body, vertices=vertices)
                pm_shapes.append(pm_shape)

        else:
            pm_shapes = [pymunk.Poly(body=self._pm_body, vertices=vertices)]

        for pm_shape in pm_shapes:
            pm_shape.friction = FRICTION_ENTITY
            pm_shape.elasticity = ELASTICITY_ENTITY

        return pm_shapes

    ##############
    # Sprites
    ##############

    def get_sprite(self, zoom: float = 1, color_uid=False) -> Sprite:

        texture = self._base_sprite.texture
        if color_uid:
            texture = self.color_with_id(texture)

        assert isinstance(texture, Texture)

        sprite = Sprite(
            texture=texture,
            scale=zoom * self._scale,
            hit_box_algorithm="Detailed",
            hit_box_detail=1,
        )

        return sprite

    def color_with_id(self, texture) -> Texture:

        img_uid = Image.new("RGBA", texture.size)
        pixels = img_uid.load()
        pixels_texture = texture.image.load()

        for i in range(img_uid.size[0]):
            for j in range(img_uid.size[1]):

                if pixels_texture[i, j] != (0, 0, 0, 0):  # type: ignore
                    pixels[i, j] = self.color_uid  # type: ignore

        texture = Texture(
            name=str(self._uid),
            image=img_uid,
            hit_box_algorithm="Detailed",
            hit_box_detail=1,
        )

        return texture

    @property
    def needs_sprite_update(self):
        return self._moved

    def update_sprite(self, view, sprite):

        pos_x = (
            self._pm_body.position.x - view.center[0]
        ) * view.zoom + view.width // 2
        pos_y = (
            self._pm_body.position.y - view.center[1]
        ) * view.zoom + view.height // 2

        sprite.set_position(pos_x, pos_y)
        sprite.angle = int(self._pm_body.angle * 180 / math.pi)

    ###################
    # Pymunk objects
    ###################

    @abstractmethod
    def _get_pm_body(self) -> pymunk.Body:
        """
        Set pymunk body. Shapes are attached to a body.
        """

    def _set_pm_collision_type(self):
        for pm_shape in self._pm_shapes:
            pm_shape.collision_type = self._collision_type

    @property
    @abstractmethod
    def _collision_type(self):
        """
        Set the collision type for the pm shapes.
        """

    def update_team_filter(self):

        for pm_shape in self._pm_shapes:
            categ = pm_shape.filter.categories

            for team_name in self._teams:
                categ = categ | 2 ** self._playground.teams[team_name]

            mask = pm_shape.filter.mask
            for team_name, team_id in self._playground.teams.items():

                if team_name not in self._teams:
                    mask = mask | 2**team_id ^ 2**team_id

            pm_shape.filter = pymunk.ShapeFilter(categories=categ, mask=mask)

    ###################
    # Position and Move
    ###################
    def move_to(
        self,
        coordinates: Union[Coordinate, CoordinateSampler],
        allow_overlapping: bool = True,
        check_within: bool = False,
    ):

        assert self._playground

        if isinstance(coordinates, CoordinateSampler):
            coordinates = self._sample_valid_coordinate()

        if (not allow_overlapping) and self._playground.overlaps(self, coordinates):
            raise ValueError("Entity overlaps but overlap is not allowed")

        if check_within and not self._playground.within_playground(
            coordinates=coordinates
        ):
            raise ValueError("Entity is not placed within Playground boundaries")

        position, angle = coordinates

        # Calculate Velocities
        absolute_velocity, angular_velocity = (0, 0), 0

        # Apply new position and velocities
        self._pm_body.position, self._pm_body.angle = position, angle
        self._pm_body.velocity = absolute_velocity
        self._pm_body.angular_velocity = angular_velocity

        if self._pm_body.space:
            self._pm_body.space.reindex_shapes_for_body(self._pm_body)

        self._moved = True

    def _sample_valid_coordinate(self) -> Coordinate:

        assert self._playground

        sampler = self._initial_coordinates
        assert isinstance(sampler, CoordinateSampler)

        for coordinate in sampler.sample():
            if not self._playground.overlaps(self, coordinate):
                return coordinate

        raise ValueError("Entity could not be placed without overlapping")

    ##############
    # PLayground Interactions
    ################

    def pre_step(self):
        self._moved = False
