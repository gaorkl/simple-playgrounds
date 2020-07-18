import math, random

from simple_playgrounds.playgrounds.empty import SingleRoom
from simple_playgrounds.entities.scene_elements import VisibleEndGoal, Basic, Apple
from simple_playgrounds.utils.position_utils import PositionAreaSampler

class Empty_01(SingleRoom):

    def __init__(self, size = (200, 800), **playground_params):

        super(Empty_01, self).__init__(size = size, **playground_params)

        endgoal_01 = VisibleEndGoal([20, 20, 0], reward=50)
        self.add_scene_element(endgoal_01)
        self.agent_starting_area = PositionAreaSampler(area_shape='circle', center=[150, 150], radius=20)


class Empty_02(SingleRoom):

    def __init__(self, size = (100, 100), **playground_params):

        super(Empty_02, self).__init__(size = size, **playground_params)

        rect = Basic([50, 50, 0], name='tada', default_config_key='circle', movable=False, mass=10, width_length=[10, 20])
        self.add_scene_element(rect)
        # rect = Basic([30, 80, 0], default_config_key='rectangle', movable=True, mass=10, width_length=[10, 20])
        # self.add_scene_element(rect)
        #
        #
        # rect = Basic([30, 60, 0], default_config_key='rectangle', movable=True, mass=10, width_length=[10, 30],
        #              texture= [250,250,250])
        # self.add_scene_element(rect)

        self.agent_starting_area = [20, 20, 0]

class Empty_Color_01(SingleRoom):

    def __init__(self, size = (200, 800), **playground_params):

        super().__init__(size = size, wall_texture = [ 120, 140, 180], **playground_params)

        endgoal_01 = VisibleEndGoal([20, 20, 0], reward=50)
        self.add_scene_element(endgoal_01)
        self.agent_starting_area = PositionAreaSampler(area_shape='circle', center=[150, 150], radius=20)



class PositionObject_01(SingleRoom):

    def __init__(self, size = (200, 200), **playground_params):

        super(PositionObject_01, self).__init__(size = size, **playground_params)

        endgoal_01 = VisibleEndGoal([20, 20, 0], reward=50)
        self.add_scene_element(endgoal_01)

        for i in range(10):
            x = 100 + 30 * math.cos(i * 2 * math.pi / 10)
            y = 100 + 30 * math.sin(i * 2 * math.pi / 10)
            theta = i * 2 * math.pi / 10

            rectangle = Basic([x, y, theta], default_config_key='rectangle', width_length = [2, 10])
            self.add_scene_element(rectangle)

class Overlap(SingleRoom):

    def __init__(self, size = (200, 200), **playground_params):

        super().__init__(size = size, **playground_params)

        area_2 = PositionAreaSampler(area_shape='circle', center=[100, 100], radius=200)

        for i in range(10):
            rectangle = Basic(area_2, default_config_key='rectangle')
            self.add_scene_element(rectangle)


class NoOverlap(SingleRoom):

    def __init__(self, size=(200, 200), **playground_params):
        super().__init__(size=size, **playground_params)

        area_2 = PositionAreaSampler(area_shape='circle', center=[100, 100], radius=200)

        for i in range(10):
            rectangle = Basic(area_2, default_config_key='rectangle')
            success = self.add_scene_element_without_overlapping(rectangle, tries=10)
            print(i, success)




class Edibles_01(SingleRoom):

    def __init__(self, size=(200, 200), **playground_params):
        super().__init__(size=size, **playground_params)

        area_2 = PositionAreaSampler(area_shape='circle', center=[100, 100], radius=200, movable = False)

        for i in range(10):
            edible = Apple(area_2)
            success = self.add_scene_element(edible)
            print(i, success)