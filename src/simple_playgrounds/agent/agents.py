import math
from simple_playgrounds.agent.agent import Agent
from simple_playgrounds.agent.part.interactives import Grasper
from simple_playgrounds.agent.part.parts import ForwardBase, Head


class HeadAgent(Agent):
    def __init__(self, playground, initial_coordinates=None, **kwargs):

        super().__init__(
            playground=playground, initial_coordinates=initial_coordinates, **kwargs
        )

        # MockTriggerPart(self._base, shape_approximation = 'decomposition')
        self.head = Head(self.base, position_on_anchor=(0, 0), rotation_range=math.pi)
        self.grasper = Grasper(self.base)

    def _add_base(self, **kwargs):
        base = ForwardBase(self, linear_ratio=10, **kwargs)
        return base
