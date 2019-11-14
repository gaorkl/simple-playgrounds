from ..default_parameters.scenes import *
import random


class SceneGenerator():

    """
    Register class to provide a decorator that is used to go through the package and
    register available scene_layouts.
    """

    subclasses = {}

    @classmethod
    def register_subclass(cls, scene_type):
        def decorator(subclass):
            cls.subclasses[scene_type] = subclass
            return subclass

        return decorator

    @classmethod
    def create(cls, scene_params):

        scene_type = scene_params['scene_type']
        if scene_type not in cls.subclasses:
            raise ValueError('Scene type not implemented:' + scene_type)

        return cls.subclasses[scene_type](scene_params)


@SceneGenerator.register_subclass('basic')
class Basic():

    def __init__(self, params):

        self.params = {**basic_scene_default, **params}

        self.width, self.length = self.params['scene_shape']

        self.walls_depth = self.params['walls_depth']
        self.walls_texture = self.params['walls_texture']

        self.wall_shapes = []
        self.generate_external_wall_shapes()

        self.entity_parameters = []
        self.generate_wall_entity_parameters()

    def generate_external_wall_shapes(self):


        self.wall_shapes.append(
            [(self.walls_depth, self.length), (self.length / 2.0, self.walls_depth / 2.0, math.pi / 2.0)])
        self.wall_shapes.append([(self.walls_depth, self.length),
                            (self.length / 2.0, self.width - self.walls_depth / 2.0, math.pi / 2.0)])
        self.wall_shapes.append(
            [(self.walls_depth, self.width), (self.walls_depth / 2.0, self.width / 2.0, 0.0)])
        self.wall_shapes.append([(self.walls_depth, self.width),
                            (self.length - self.walls_depth / 2.0, self.width / 2.0, 0.0)])


    def generate_wall_entity_parameters(self):

        wall = {
            'entity_type': 'basic',
            'physical_shape': 'rectangle',
            'movable': False,

        }

        for wall_shape in self.wall_shapes:
            depth_length, position = wall_shape
            wall['shape_rectangle'] = depth_length
            wall['position'] = position
            wall['texture'] = self.walls_texture

            self.entity_parameters.append(wall.copy())

@SceneGenerator.register_subclass('two_rooms')
class TwoRooms(Basic):

    def __init__(self, params):

        self.params = {**two_rooms_scene_default, **params}

        self.doorstep_type = self.params['doorstep_type']
        self.doorstep_size = self.params['doorstep_size']

        super(TwoRooms, self).__init__( params)

        self.position_doorstep = []

        self.internal_walls_shapes = []
        self.generate_internal_walls_shapes()

        self.generate_internal_walls_entity_parameters()

    def generate_internal_walls_shapes(self):

        if self.doorstep_type == 'random':
            self.position_doorstep = [self.length / 2.0 , random.uniform( self.doorstep_size / 2, self.width - self.doorstep_size / 2) ]

        else:
            raise ValueError( 'Doorstep type not implemented ')

        #TODO: check rounding errors
        right_wall = [(self.walls_depth, self.position_doorstep[1] - self.doorstep_size / 2),
                      (self.length / 2.0, ((self.position_doorstep[1] - self.doorstep_size / 2) / 2.0), 0)]

        coord_center_wall_left =  self.position_doorstep[1] + self.doorstep_size / 2 + (self.width - (self.position_doorstep[1] + self.doorstep_size / 2))/2.0
        left_wall = [(self.walls_depth, self.width - (self.position_doorstep[1] + self.doorstep_size / 2)),
                      (self.length / 2.0,coord_center_wall_left, 0)]

        self.internal_walls_shapes.append(left_wall)
        self.internal_walls_shapes.append(right_wall)

    def generate_internal_walls_entity_parameters(self):

        wall = {
            'entity_type': 'basic',
            'physical_shape': 'rectangle',
            'movable': False,

        }

        for wall_shape in self.internal_walls_shapes:
            depth_length, position = wall_shape
            wall['shape_rectangle'] = depth_length
            wall['position'] = position
            wall['texture'] = self.walls_texture

            self.entity_parameters.append(wall.copy())