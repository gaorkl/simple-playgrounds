from spg.components.grasper import GraspableMixin
from spg.core.entity import Element
from spg.core.entity.mixin import BaseDynamicMixin


class Ball(Element, BaseDynamicMixin):
    def __init__(self):

        super().__init__(
            mass=10,
            filename=":spg:rollingball/ball/ball_blue_large.png",
            radius=10,
        )


class GraspableBall(Ball, GraspableMixin):
    pass
