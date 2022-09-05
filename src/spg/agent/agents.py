import math
from .part import ForwardBase, Head
from .interactor import Grasper
from .agent import Agent


class HeadAgent(Agent):
    def __init__(self, **kwargs):

        super().__init__(**kwargs)

        base = ForwardBase(linear_ratio=10)
        self.add(base)

        self.head = Head(rotation_range=math.pi)
        base.add(self.head)

        self.grasper = Grasper(base)
        base.add(self.grasper)

        self.grasp_controller = self.grasper.grasp_controller
        base.add(self.grasp_controller)
