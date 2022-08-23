from simple_playgrounds.playground.playground import Playground
from simple_playgrounds.element.wall import (
    create_wall_from_blocks,
    BrickWallBlock,
)
from typing import Tuple


class WallClosedPG(Playground):
    def __init__(self, size: Tuple[int, int], seed=None, background=None):
        super().__init__(size, seed, background)

        assert self._width
        assert self._height

        pts = [
            [
                (-self._width / 2, -self._height / 2),
                (-self._width / 2, self._height / 2),
            ],
            [(-self._width / 2, self._height / 2), (self._width / 2, self._height / 2)],
            [(self._width / 2, self._height / 2), (self._width / 2, -self._height / 2)],
            [
                (self._width / 2, -self._height / 2),
                (-self._width / 2, -self._height / 2),
            ],
        ]

        for begin_pt, end_pt in pts:

            create_wall_from_blocks(self, BrickWallBlock, begin_pt, end_pt, width=10)
