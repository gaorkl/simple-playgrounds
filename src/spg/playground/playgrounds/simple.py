from typing import Tuple

from ...element.wall import BrickWallBlock, ColorWall, create_wall_from_blocks
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


class WallClosedColorPG(Playground):
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

            random_color = list(self._rng.integers(0, 255, 3))
            random_color.append(255)
            wall = ColorWall(begin_pt, end_pt, width=10, color=tuple(random_color))
            self.add(wall, wall.wall_coordinates)
