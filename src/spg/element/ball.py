from .element import PhysicalElement


class Ball(PhysicalElement):
    def __init__(self):

        super().__init__(
            mass=10,
            filename=":spg:rollingball/ball/ball_blue_large.png",
            radius=10,
        )

    def _set_pm_collision_type(self):
        pass
