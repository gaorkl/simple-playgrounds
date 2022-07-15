from __future__ import annotations


from abc import ABC
from typing import Optional
from arcade.application import View
from matplotlib.pyplot import text

import pymunk
from skimage.draw import disk, polygon
import tripy
import numpy as np

from PIL import Image

from simple_playgrounds.entity.entity import Entity

import math
from abc import ABC, abstractmethod
from typing import Optional, TYPE_CHECKING, Dict
from arcade import Texture, Sprite


if TYPE_CHECKING:
    from simple_playgrounds.playground.playground import Playground

from simple_playgrounds.common.definitions import FRICTION_ENTITY, ELASTICITY_ENTITY

from simple_playgrounds.common.position_utils import (
    CoordinateSampler,
    InitCoord,
    Coordinate,
)


class EmbodiedEntity(Entity, ABC):

    """
    Embodied Entities are elementary entities physically present in the playground.
    They can interact with other Embodied Entities through
    pymunk collisions.

    """

    def __init__(
        self,
        playground: Playground,
        initial_coordinates: InitCoord,
        filename: Optional[str] = None,
        texture: Optional[Texture] = None,
        radius: Optional[float] = None,
        width: Optional[float] = None,
        height: Optional[float] = None,
        pm_shape: Optional[pymunk.Shape] = None,
        color: Optional[pymunk.Shape] = None,
        temporary: bool = False,
        allow_overlapping: bool = True,
        shape_approximation: Optional[str] = None,
        sprite_front_is_up: bool = False,
        **kwargs,
    ):

        self._required_sprites_update: Dict[Sprite, bool] = {}

        self._pm_from_sprite = False
        self._pm_from_shape = False

        self._sprite_front_is_up = sprite_front_is_up

        if filename or texture:
            self._pm_from_sprite = True

            self._base_sprite = Sprite(texture=texture, filename=filename, hit_box_algorithm="Detailed", hit_box_detail=1, flipped_diagonally=sprite_front_is_up, flipped_horizontally=sprite_front_is_up)  # type: ignore

            (
                self._scale,
                self._radius,
                self._width,
                self._height,
            ) = self._apply_scale(radius, width, height)
            self._pm_body = self._get_pm_body()
            self._pm_shapes = self._get_pm_shapes_from_sprite(shape_approximation)

        elif pm_shape:
            self._pm_from_shape = True
            self._pm_body = self._get_pm_body(pm_shape)
            pm_shape.body = self._pm_body
            self._pm_shapes = [pm_shape]

        else:
            raise ValueError("Filename, texture or pm_shape should be specified")

        super().__init__(playground, **kwargs)

        if pm_shape:
            texture = self._get_texture_from_shape(pm_shape, color)
            self._base_sprite = Sprite(texture=texture, hit_box_algorithm="Detailed", hit_box_detail=1)  # type: ignore
            (
                self._scale,
                self._radius,
                self._width,
                self._height,
            ) = self._apply_scale(radius, width, height)

        self._add_to_pymunk_space()
        self._playground.add_to_views(self)

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
    def sprite_front_is_up(self):
        return self._sprite_front_is_up

    @property
    def playground(self):
        return self._playground

    @property
    def radius(self):
        return self._radius

    @property
    def width(self):
        return self._width

    @property
    def height(self):
        return self._height

    @property
    def size(self):
        return self._width, self._height

    @property
    def texture(self):
        return self._base_sprite.texture

    @property
    def pm_shapes(self):
        return self._pm_shapes

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

        elif self._pm_body.body_type == pymunk.Body.DYNAMIC:

            vel = self._pm_body.velocity.height
            if vel > 0.1:
                return True

            ang_vel = self._pm_body.angular_velocity
            if ang_vel > 0.01:
                return True

        return False

    ##############
    # Init pm Elements
    ###############

    def _get_texture_from_shape(self, pm_shape, color):

        color_rgba = [c for c in color] + [255]

        if isinstance(pm_shape, pymunk.Segment):
            radius = int(pm_shape.radius)
            length = int((pm_shape.a - pm_shape.b).length)
            img = np.zeros((radius, length, 4))
            img[:, :] = color_rgba

        elif isinstance(pm_shape, pymunk.Circle):
            radius = int(pm_shape.radius)

            img = np.zeros((2 * radius + 1, 2 * radius + 1, 4))
            rr, cc = disk((radius, radius), radius)
            img[rr, cc] = color_rgba

        elif isinstance(pm_shape, pymunk.Poly):
            vertices = pm_shape.get_vertices()

            top = max([vert[0] for vert in vertices])
            bottom = min([vert[0] for vert in vertices])
            left = min([vert[1] for vert in vertices])
            right = max([vert[1] for vert in vertices])

            w = int(right - left)
            h = int(top - bottom)

            center = int(h / 2), int(w / 2)

            img = np.zeros((h, w, 4))
            r = [y + center[0] for x, y in vertices]
            c = [x + center[1] for x, y in vertices]

            rr, cc = polygon(r, c, (h, w))

            img[rr, cc] = color_rgba

        else:
            raise ValueError

        PIL_image = Image.fromarray(np.uint8(img)).convert("RGBA")

        texture = Texture(
            name="Shape_%i".format(self._uid),
            image=PIL_image,
            hit_box_algorithm="Detailed",
            hit_box_detail=1,
        )

        return texture

    def _apply_scale(self, radius, width, height):

        orig_radius = max(
            [pymunk.Vec2d(*vert).length for vert in self._base_sprite.get_hit_box()]
        )

        horiz = [pymunk.Vec2d(*vert).x for vert in self._base_sprite.get_hit_box()]
        vert = [pymunk.Vec2d(*vert).y for vert in self._base_sprite.get_hit_box()]

        orig_width = max(horiz) - min(horiz)
        orig_height = max(vert) - min(vert)

        # If radius imposed:
        if radius:
            scale = radius / orig_radius

        elif height:
            scale = height / orig_height

        elif width:
            scale = width / orig_width
        else:
            scale = 1

        width = scale * orig_width
        height = scale * orig_height
        radius = scale * orig_radius

        return scale, radius, width, height

    def _get_pm_shapes_from_sprite(self, shape_approximation):

        vertices = self._base_sprite.get_hit_box()

        vertices = [(x * self._scale, y * self._scale) for x, y in vertices]

        if shape_approximation == "circle":
            pm_shapes = [pymunk.Circle(self._pm_body, self._radius)]

        elif shape_approximation == "box":
            top = max([vert[0] for vert in vertices])
            bottom = min([vert[0] for vert in vertices])
            left = min([vert[1] for vert in vertices])
            right = max([vert[1] for vert in vertices])

            box_vertices = ((top, left), (top, right), (bottom, right), (bottom, left))

            pm_shapes = [pymunk.Poly(self._pm_body, box_vertices)]

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

    def _get_physical_scale(self, radius):

        orig_radius = max(
            [pymunk.Vec2d(*vert).height for vert in self._base_sprite.get_hit_box()]
        )

        if not radius:
            return 1, orig_radius

        physical_scale = radius / orig_radius

        return physical_scale, radius

    def get_sprite(self, zoom: float = 1) -> Sprite:

        texture = self._base_sprite.texture
        assert isinstance(texture, Texture)

        sprite = Sprite(
            texture=texture,
            scale=zoom * self._scale,
            hit_box_algorithm="Detailed",
            hit_box_detail=1,
        )
        self._required_sprites_update[sprite] = True
        return sprite

    def get_id_sprite(self, zoom: float = 1) -> Sprite:

        base_texture = self._base_sprite.texture
        assert isinstance(base_texture, Texture)

        img_uid = Image.new("RGBA", base_texture.size)
        pixels = img_uid.load()
        pixels_texture = base_texture.image.load()

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

        sprite = Sprite(
            texture=texture,
            scale=zoom * self._scale,
            hit_box_algorithm="Detailed",
            hit_box_detail=1,
        )

        self._required_sprites_update[sprite] = True
        return sprite

    def update_sprite(self, view, sprite, force=False):

        if self._required_sprites_update[sprite] or force:

            pos_x = (
                self._pm_body.position.x - view.center[0]
            ) * view.zoom + view.width // 2
            pos_y = (
                self._pm_body.position.y - view.center[1]
            ) * view.zoom + view.height // 2

            sprite.set_position(pos_x, pos_y)
            sprite.angle = int(self.pm_body.angle * 180 / math.pi)

            self._required_sprites_update[sprite] = False

    ###################
    # Pymunk objects
    ###################

    @abstractmethod
    def _get_pm_body(self, *_) -> pymunk.Body:
        """
        Set pymunk body. Shapes are attached to a body.
        """
        ...

    def _add_to_pymunk_space(self):
        self._playground.space.add(self._pm_body, *self._pm_shapes)

    def _remove_from_pymunk_space(self):
        self._playground.space.remove(self._pm_body, *self._pm_shapes)

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

        for pm_shape in self._pm_shapes:
            categ = pm_shape.filter.categories

            for team in self._teams:
                categ = categ | 2 ** self._playground.teams[team]

            mask = pm_shape.filter.mask
            for team in self._playground.teams:

                if team not in self._teams:
                    mask = (
                        mask
                        | 2 ** self._playground.teams[team]
                        ^ 2 ** self._playground.teams[team]
                    )

            pm_shape.filter = pymunk.ShapeFilter(categories=categ, mask=mask)

    ###################
    # Position and Move
    ###################

    def move_to(
        self,
        coordinates: Coordinate,
        allow_overlapping: bool = True,
        keep_velocity: bool = False,
    ):

        if (not allow_overlapping) and self._playground.overlaps(self, coordinates):
            raise ValueError("Entity overlaps but should not")

        if not self._playground.within_playground(coordinates):
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
        self._required_sprites_update = dict.fromkeys(
            self._required_sprites_update, True
        )

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
            raise ValueError("Initial Coordinate is not set")

        self.move_to(
            coordinates, allow_overlapping=self._allow_overlapping, keep_velocity=False
        )

    def _sample_valid_coordinate(self) -> Coordinate:

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

    def remove(self, definitive: bool = False):

        self._remove_from_pymunk_space()
        self._playground.remove_from_views(self)
        super().remove(definitive=definitive or self._temporary)

    def reset(self):

        # Remove completely if temporary
        if self._temporary:
            self.remove()
            return

        if self._removed:
            self._add_to_pymunk_space()
            self._playground.add_to_views(self)

        self._move_to_initial_coordinates()
        self._removed = False

    def post_step(self):

        if self.moved:

            self._required_sprites_update = dict.fromkeys(
                self._required_sprites_update, True
            )
