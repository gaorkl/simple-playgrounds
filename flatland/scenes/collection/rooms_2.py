import math

from ..register import SceneGenerator
from .basic import BasicScene



@SceneGenerator.register_subclass('rooms_2')
class TwoRooms(BasicScene):

    def __init__(self, params):

        # Overwrite basic params if needed
        super(TwoRooms, self).__init__(params)

        wall_shape = [(self.walls_depth, self.total_area[0] * 3 / 4 - 2*self.walls_depth),
                       (self.total_area[0] * 3 / 8.0, self.total_area[1] / 2.0, math.pi / 2.0)]

        # TODO: fctorize wall
        wall = {}
        wall['entity_type'] = 'basic'
        wall['physical_shape'] = 'box'
        wall['size_box'] = wall_shape[0]
        wall['position'] = wall_shape[1]
        wall['movable'] = False
        wall['debug_color'] = (200, 0, 0)

        self.elements.append(wall)
