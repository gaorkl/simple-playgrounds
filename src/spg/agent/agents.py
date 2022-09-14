import math

from .agent import Agent
from .part import ForwardBase, Head


class HeadAgent(Agent):
    def __init__(self, **kwargs):

        super().__init__(**kwargs)

        base = ForwardBase(linear_ratio=10)
        self.add(base)

        self.head = Head(rotation_range=math.pi)
        base.add(self.head)

        self.base.add_grasper()
