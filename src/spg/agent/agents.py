import math

from .agent import Agent
from .communicator import Communicator
from .part import ForwardBase, Head
from .sensor import DistanceSensor, RGBSensor


class HeadAgent(Agent):
    def __init__(self, **kwargs):

        super().__init__(**kwargs)

        base = ForwardBase(linear_ratio=10)
        self.add(base)

        self.head = Head(rotation_range=math.pi)
        base.add(self.head)

        # SENSORS
        self.distance = DistanceSensor(
            fov=360, resolution=36, range=100, invisible_elements=self._parts
        )
        self.base.add(self.distance)

        self.rgb = RGBSensor(
            fov=90, resolution=64, range=400, invisible_elements=self._parts
        )
        self.head.add(self.rgb)

        # COMMS
        self.comm = Communicator()
        self.base.add(self.comm)

        self.base.add_grasper()
