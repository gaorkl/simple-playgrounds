import math

from .agent import Agent
from .communicator import Communicator
from .interactor import GraspHold
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
            fov=360,
            resolution=36,
            max_range=100,
            invisible_elements=self._parts,
            normalize=True,
        )
        self.base.add(self.distance)

        self.rgb = RGBSensor(
            fov=180,
            resolution=64,
            max_range=400,
            invisible_elements=self._parts,
            invisible_when_grasped=True,
        )
        self.head.add(self.rgb)

        # COMMS
        self.comm = Communicator()
        self.base.add(self.comm)

        # Grapser
        grasp = GraspHold(base)
        self.base.add(grasp)
