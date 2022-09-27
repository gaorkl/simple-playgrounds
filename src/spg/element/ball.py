from typing import Optional, Tuple

from .element import PhysicalElement


class Ball(PhysicalElement):
    def __init__(self, color: Optional[Tuple[int, int, int]] = None):

        super().__init__(
            mass=10,
            filename=":spg:rollingball/ball/ball_blue_large.png",
            radius=10,
            color=color,
        )

    def _set_pm_collision_type(self):
        pass
