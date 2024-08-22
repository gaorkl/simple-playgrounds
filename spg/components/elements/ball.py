from spg.core.entity import Element
from spg.core.entity.body import BaseDynamicMixin
from spg.core.entity.interaction.grasper import GraspableMixin


class Ball(Element, BaseDynamicMixin):
    def __init__(self):

        super().__init__(
            mass=10,
            filename=":resources:onscreen_controls/shaded_light/b.png",
            radius=10,
        )


class GraspableBall(Ball, GraspableMixin):
    pass
