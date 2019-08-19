import math

from ..register import SceneGenerator
from flatland.scenes.collection.room import BasicScene



@SceneGenerator.register_subclass('rooms_2')
class TwoRooms(BasicScene):

    def __init__(self, params):

        # Overwrite basic params if needed
        super(TwoRooms, self).__init__(params)

        wall_shapes = []

        wall_shapes.append([(self.walls_depth, self.total_area[1] * 1 / 3),
                            (self.total_area[1] * 1 / 6.0, self.total_area[0] / 2.0, math.pi / 2.0)])
        wall_shapes.append([(self.walls_depth, self.total_area[1] * 1 / 3),
                            (self.total_area[1] * 5 / 6.0, self.total_area[0] / 2.0, math.pi / 2.0)])

        # TODO: fctorize wall
        wall = {
            'entity_type': 'basic',
            'physical_shape': 'rectangle',
            'movable' : False,
            'texture' : self.walls_texture
            }

        for wall_shape in wall_shapes:

            wall['shape_rectangle'] = wall_shape[0]
            wall['position'] = wall_shape[1]


            self.elements.append(wall.copy())
