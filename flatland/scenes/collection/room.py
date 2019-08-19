import math

from flatland.scenes.register import SceneGenerator

from flatland.common.default_scene_parameters import *



@SceneGenerator.register_subclass('room')
class BasicScene():

    def __init__(self, params ):

        # Overwrite basic params if needed
        self.params = {**basic_scene_default, **params}

        self.walls_texture = self.params['walls_texture']
        self.walls_depth = self.params['walls_depth']
        self.total_area = self.params['shape']

        self.generate_walls()

    def generate_walls(self):
        '''
        Generate coordinates for walls as rectangles.
        :param params:
        :return:
        '''

        wall_shapes = []
        wall_shapes.append(
            [(self.walls_depth, self.total_area[1]), (self.total_area[1] / 2.0, self.walls_depth / 2.0, math.pi / 2.0)])
        wall_shapes.append([(self.walls_depth, self.total_area[1]),
                             (self.total_area[1] / 2.0, self.total_area[0] - self.walls_depth / 2.0, math.pi / 2.0)])
        wall_shapes.append(
            [(self.walls_depth, self.total_area[0]), (self.walls_depth / 2.0, self.total_area[0] / 2.0, 0.0)])
        wall_shapes.append([(self.walls_depth, self.total_area[0]),
                            (self.total_area[1] - self.walls_depth / 2.0, self.total_area[0] / 2.0, 0.0)])

        self.elements = []

        wall = {
            'entity_type': 'basic',
            'physical_shape': 'rectangle',
            'movable': False,
            'texture': self.walls_texture,

        }

        for wall_shape in wall_shapes:
            depth_length, position = wall_shape
            wall['shape_rectangle'] = depth_length
            wall['position'] = position

            self.elements.append(wall.copy())

