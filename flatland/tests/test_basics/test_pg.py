import math, random

from flatland.playgrounds.empty import SingleRoom
from flatland.entities import VisibleEndGoal, Basic
from flatland.utils.position_utils import PositionAreaSampler

class Empty_01(SingleRoom):

    def __init__(self, size = (200, 800), **playground_params):

        super(Empty_01, self).__init__(size = size, **playground_params)

        endgoal_01 = VisibleEndGoal([20, 20, 0], reward=50)
        self.add_entity(endgoal_01)
        self.agent_starting_area = PositionAreaSampler(area_shape='circle', center=[150, 150], radius=20)



class PositionObject_01(SingleRoom):

    def __init__(self, size = (200, 200), **playground_params):

        super(PositionObject_01, self).__init__(size = size, **playground_params)

        endgoal_01 = VisibleEndGoal([20, 20, 0], reward=50)
        self.add_entity(endgoal_01)

        for i in range(10):
            x = 100 + 30 * math.cos(i * 2 * math.pi / 10)
            y = 100 + 30 * math.sin(i * 2 * math.pi / 10)
            theta = i * 2 * math.pi / 10

            rectangle = Basic([x, y, theta], default_config_key='rectangle', width_length = [2, 10])
            self.add_entity(rectangle)

class Overlap(SingleRoom):

    def __init__(self, size = (200, 200), **playground_params):

        super().__init__(size = size, **playground_params)

        area_2 = PositionAreaSampler(area_shape='circle', center=[100, 100], radius=200)

        for i in range(10):
            rectangle = Basic(area_2, default_config_key='rectangle')
            self.add_entity(rectangle)


class NoOverlap(SingleRoom):

    def __init__(self, size=(200, 200), **playground_params):
        super().__init__(size=size, **playground_params)

        area_2 = PositionAreaSampler(area_shape='circle', center=[100, 100], radius=200)

        for i in range(10):
            rectangle = Basic(area_2, default_config_key='rectangle')
            success = self.add_entity_without_overlappig(rectangle)
            print(i, success)