from typing import Tuple

from ...element.wall import BrickWallBlock, create_wall_from_blocks
from ..playground import Playground


class WallClosedPG(Playground):
    def __init__(self, size: Tuple[int, int], seed=None, background=None):
        super().__init__(size, seed, background)

        assert isinstance(self._width, int)
        assert isinstance(self._height, int)

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
