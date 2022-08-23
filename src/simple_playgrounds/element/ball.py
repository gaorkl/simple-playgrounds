from simple_playgrounds.entity.physical import PhysicalEntity


from simple_playgrounds.playground.playground import Playground

from simple_playgrounds.common.position_utils import InitCoord


class Ball(PhysicalEntity):
    def __init__(self):

        super().__init__(
            mass=10,
            filename=":spg:rollingball/ball/ball_blue_large.png",
            radius=10,
        )

    def _set_pm_collision_type(self):
        pass
