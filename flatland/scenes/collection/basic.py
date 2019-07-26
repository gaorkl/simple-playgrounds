import math

from ..register import SceneGenerator


basic_params = {
    'scene_type': 'basic',
    'shape': (400, 400),
    'walls_depth': 10,
    'walls_texture':
        {
        'texture_type': 'color',
        'color': (124, 110, 1)
        }
    }


@SceneGenerator.register_subclass('basic')
class BasicScene():

    def __init__(self, params ):

        # Overwrite basic params if needed
        self.params = {**basic_params, **params}

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
            [(self.walls_depth, self.total_area[0]), (self.total_area[0] / 2.0, self.walls_depth / 2.0, math.pi / 2.0)])
        wall_shapes.append([(self.walls_depth, self.total_area[0]),
                            (self.total_area[0] / 2.0, self.total_area[1] - self.walls_depth / 2.0, math.pi / 2.0)])
        wall_shapes.append(
            [(self.walls_depth, self.total_area[1]), (self.walls_depth / 2.0, self.total_area[1] / 2.0, 0.0)])
        wall_shapes.append([(self.walls_depth, self.total_area[1]),
                            (self.total_area[0] - self.walls_depth / 2.0, self.total_area[1] / 2.0, 0.0)])

        self.elements = []
        for wall_shape in wall_shapes:
            depth_length, position = wall_shape
            wall = {}
            wall['entity_type'] = 'basic'
            wall['physical_shape'] = 'box'
            wall['size_box'] = wall_shape[0]
            wall['position'] = wall_shape[1]
            wall['movable'] = False
            wall['debug_color'] = (200, 0, 0)

            self.elements.append(wall)

