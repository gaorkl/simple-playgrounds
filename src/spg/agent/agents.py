import math

from .agent import Agent
from .part import ForwardBase, Head
from .sensor import DistanceSensor, RGBSensor


class HeadAgent(Agent):
    def __init__(self, **kwargs):

        super().__init__(**kwargs)

        base = ForwardBase(linear_ratio=10)
        self.add(base)

        self.head = Head(rotation_range=math.pi)
        base.add(self.head)

        self.distance = DistanceSensor(
            fov=360, resolution=36, range=100, invisible_elements=self._parts
        )

        self.base.add(self.distance)

        self.rgb = RGBSensor(
            fov=90,
            resolution=64,
            range=400,
            invisible_elements=self._parts,
            invisible_when_grasped=True,
        )

        self.head.add(self.rgb)

        self.base.add_grasper()
