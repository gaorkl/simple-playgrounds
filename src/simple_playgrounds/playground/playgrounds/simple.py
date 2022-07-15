from simple_playgrounds.playground.playground import ClosedPlayground
from simple_playgrounds.element.basic.wall import (
    create_wall_from_blocks,
    BrickWallBlock,
)
from typing import Tuple


class WallClosedPG(ClosedPlayground):
    def __init__(self, size: Tuple[int, int], seed=None, background=None):
        super().__init__(size, seed, background)

        pts = [
            [(-self.width / 2, -self.height / 2), (-self._width / 2, self.height / 2)],
            [(-self.width / 2, self.height / 2), (self._width / 2, self.height / 2)],
            [(self.width / 2, self.height / 2), (self._width / 2, -self.height / 2)],
            [(self.width / 2, -self.height / 2), (-self._width / 2, -self.height / 2)],
        ]

        for begin_pt, end_pt in pts:

            create_wall_from_blocks(self, BrickWallBlock, begin_pt, end_pt, width=10)
