import math

from .agent import Agent
from .device.interactor import GraspHold
from .part import ForwardBase, Head
from .device.sensor import DistanceSensor, RGBSensor


class HeadAgent(Agent):
    def __init__(self, **kwargs):

        super().__init__(**kwargs)

        self.head = Head(name='head', rotation_range=math.pi)
        self.base.add(self.head)

        # SENSORS
        self.distance = DistanceSensor(
            name='distance',
            fov=360,
            resolution=36,
            max_range=100,
            invisible_elements=self._parts,
            normalize=True,
        )
        self.base.add(self.distance)

        self.rgb = RGBSensor(
            name='rgb',
            fov=180,
            resolution=64,
            max_range=400,
            invisible_elements=self._parts,
            invisible_when_grasped=True,
        )
        self.head.add(self.rgb)

        # Grapser
        grasp = GraspHold(self.base, name='grasp')
        self.base.add(grasp)

    def _get_base(self):
        base = ForwardBase(name='base', linear_ratio=10)
        return base
