from abc import ABC
from simple_playgrounds.entity.physical import PhysicalEntity
from simple_playgrounds.playground.playground import Playground
import pymunk
from PIL import Image
import numpy as np
from typing import Type
from arcade.texture import Texture


class WallBlock(PhysicalEntity, ABC):
    def __init__(self, playground: Playground, initial_coordinates, filename, **kwargs):
        super().__init__(playground, initial_coordinates, filename=filename, **kwargs)

    def _set_pm_collision_type(self):
        pass


def create_wall_from_blocks(
    playground: Playground,
    wall_block_cls: Type[WallBlock],
    pos_start,
    pos_end,
    width,
    border_wall_block=2,
):
    length = (pymunk.Vec2d(*pos_start) - pos_end).length
    orientation = (pymunk.Vec2d(*pos_end) - pos_start).angle

    position = (pymunk.Vec2d(*pos_start) + pos_end) / 2

    n_blocks = int(length / (width - 2 * border_wall_block))

    wall_block_cls(playground, (pos_end, orientation), width=width)

    for index_block in range(n_blocks + 1):

        position = (
            pymunk.Vec2d(*pos_start)
            + pymunk.Vec2d(1, 0).rotated(orientation)
            * (width - border_wall_block)
            * index_block
        )

        wall_block_cls(playground, (position, orientation), width=width)


class BrickWallBlock(WallBlock):
    def __init__(self, playground: Playground, initial_coordinates, **kwargs):

        fname = ":spg:platformer/tiles/wall_grey.png"
        super().__init__(playground, initial_coordinates, filename=fname, **kwargs)


class ColorWall(PhysicalEntity):
    def __init__(self, playground, pos_start, pos_end, width, color, **kwargs):

        length = (pymunk.Vec2d(*pos_start) - pos_end).length + width

        position = (pymunk.Vec2d(*pos_start) + pos_end) / 2
        orientation = (pymunk.Vec2d(*pos_end) - pos_start).angle

        img = Image.new("RGBA", (int(width), int(length)), color)

        texture = Texture(
            name="Barrier_%i_%i".format(int(width), int(length)),
            image=img,
            hit_box_algorithm="Detailed",
            hit_box_detail=1,
        )

        super().__init__(playground, (position, orientation), texture=texture, **kwargs)

    def _get_pm_shapes(self, *_):
        return [
            pymunk.Segment(
                self._pm_body,
                (-self._height / 2, 0),
                (self._height / 2, 0),
                self._width,
            )
        ]

    @property
    def length(self):
        return self.height

    def _set_pm_collision_type(self):
        pass
