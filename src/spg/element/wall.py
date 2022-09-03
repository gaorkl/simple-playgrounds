from __future__ import annotations
from abc import ABC

from typing import Type, TYPE_CHECKING
import pymunk
from PIL import Image
import math
from arcade.texture import Texture

from spg.element.element import PhysicalElement


if TYPE_CHECKING:
    from ..playground import Playground


class WallBlock(PhysicalElement, ABC):
    def __init__(self, filename, **kwargs):
        super().__init__(filename=filename, **kwargs)


def create_wall_from_blocks(
    playground: Playground, wall_block_cls: Type[WallBlock], pos_start, pos_end, width
):
    length = (pymunk.Vec2d(*pos_start) - pos_end).length
    orientation = (pymunk.Vec2d(*pos_end) - pos_start).angle

    position = (pymunk.Vec2d(*pos_start) + pos_end) / 2

    n_blocks = int(length / width)

    wall_block = wall_block_cls(width=width)
    playground.add(wall_block, (pos_end, orientation))

    for index_block in range(n_blocks):

        block_position = (
            pymunk.Vec2d(*pos_start)
            + pymunk.Vec2d(1, 0).rotated(orientation) * width * index_block
        )

        wall_block = wall_block_cls(width=width)
        playground.add(wall_block, (block_position, orientation))

    # wall_block = wall_block_cls(width=width)
    # playground.add(wall_block, (pos_end, orientation))


class BrickWallBlock(WallBlock):
    def __init__(self, **kwargs):

        fname = ":spg:platformer/tiles/wall_grey.png"
        super().__init__(filename=fname, **kwargs)


class ColorWall(PhysicalElement):
    def __init__(self, pos_start, pos_end, width, color, **kwargs):

        length = (pymunk.Vec2d(*pos_start) - pos_end).length + width

        position = (pymunk.Vec2d(*pos_start) + pos_end) / 2
        angle = (pymunk.Vec2d(*pos_end) - pos_start).angle + math.pi / 2

        self.wall_coordinates = position, angle

        img = Image.new("RGBA", (int(width), int(length)), color)

        texture = Texture(
            name="Barrier_%i_%i".format(int(width), int(length)),
            image=img,
            hit_box_algorithm="Detailed",
            hit_box_detail=1,
        )

        super().__init__(texture=texture, **kwargs)
