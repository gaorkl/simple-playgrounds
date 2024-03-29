from __future__ import annotations

import math
from abc import ABC, abstractmethod

import numpy as np
import pymunk
from arcade.resources import resolve_resource_path
from arcade.texture import Texture
from PIL import Image
from skimage.io import imread
from skimage.transform import resize

from spg.core.entity import Element
from spg.core.entity.mixin import BaseStaticMixin

WALL_WIDTH = 10


class Wall(Element, BaseStaticMixin):
    def __init__(self, pos_start, pos_end, color, wall_width=WALL_WIDTH, **kwargs):

        wall_length = (pymunk.Vec2d(*pos_start) - pos_end).length

        position = (pymunk.Vec2d(*pos_start) + pos_end) / 2
        angle = (pymunk.Vec2d(*pos_end) - pos_start).angle + math.pi / 2

        self.wall_coordinates = position, angle

        img = self._get_img_wall(wall_width, wall_length)

        texture = Texture(
            name=f"{type(self)}_{wall_width}_{wall_length}",
            image=img,
            hit_box_algorithm="None",
            hit_box_detail=1,
        )

        super().__init__(texture=texture, color_tint=color, **kwargs)

    @abstractmethod
    def _get_img_wall(self, wall_width, wall_length):
        ...


class ColorWall(Wall):
    def _get_img_wall(self, width, length):
        return Image.new("RGBA", (int(width), int(length)), (255, 255, 255, 255))


class TiledColorWall(Wall, ABC):
    _fname: str

    def _get_img_wall(self, width, length):

        file_name = resolve_resource_path(self._fname)

        tile_array = imread(file_name)

        length_resize = tile_array.shape[1] * width / tile_array.shape[0]
        tile_array = resize(tile_array, (width, length_resize))

        n_repeats = int(length / tile_array.shape[0]) + 1
        new_img = np.tile(tile_array, reps=(1, n_repeats, 1))
        new_img = (new_img[:, : int(length), :] * 255).astype(np.uint8)
        new_img = new_img.swapaxes(1, 0)

        return Image.fromarray(new_img)


class TiledAlternateColorWall(TiledColorWall):
    _fname = ":spg:spg/tile_alternate.png"


class TiledGradientColorWall(TiledColorWall):
    _fname = ":spg:spg/tile_grad.png"


class TiledLongColorWall(TiledColorWall):
    _fname = ":spg:spg/tile_long.png"
