import math


class SceneGenerator():
    subclasses = {}

    @classmethod
    def register_subclass(cls, scene_type):
        def decorator(subclass):
            cls.subclasses[scene_type] = subclass
            return subclass

        return decorator

    @classmethod
    def create(cls, params):
        scene_type = params['scene_type']
        if scene_type not in cls.subclasses:
            raise ValueError('Scene type not implemented:' + scene_type)

        return cls.subclasses[scene_type](params)


@SceneGenerator.register_subclass('basic')
class BasicScene():

    def __init__(self, params):
        self.walls_depth = params['walls_depth']

        self.total_area = params['shape']

        self.generate_walls(params)

    def generate_walls(self, params):
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


@SceneGenerator.register_subclass('2-rooms')
class TwoRooms(BasicScene):

    def __init__(self, params):
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
