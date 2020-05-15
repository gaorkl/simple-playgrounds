import yaml
import math
import os
from flatland.entities.basic import Basic

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


        scene_type = scene_params.get('scene_type')

        if scene_type is None:
            raise ValueError('Scene type not specified')

        if scene_type not in cls.subclasses:
            raise ValueError('Scene type not implemented:' + scene_type)

        return cls.subclasses[scene_type](scene_params)


class Scene():

    def __init__(self, custom_config):

        self.config = custom_config
        self.width, self.length = self.config['scene_shape']

        self.wall_depth = self.config['wall']['depth']

        self.scene_entities = []


    def generate_external_wall_shapes(self):
        """
        Generate list of (length, (position x, position y)) for walls around the scene

        :return:
        """
        walls = []

        walls.append([ self.length, (0, self.length / 2.0, math.pi / 2.0)])
        walls.append([ self.length, (self.width , self.length / 2.0,  math.pi / 2.0)])
        walls.append([ self.width, ( self.width / 2.0, 0, 0.0)])
        walls.append([ self.width, ( self.width / 2.0, self.length , 0.0)])
        # walls.append([ self.length, (self.wall_depth / 2.0, self.length / 2.0, math.pi / 2.0)])
        # walls.append([ self.length, (self.width - self.wall_depth / 2.0, self.length / 2.0,  math.pi / 2.0)])
        # walls.append([ self.width, ( self.width / 2.0, self.wall_depth / 2.0, 0.0)])
        # walls.append([ self.width, ( self.width / 2.0, self.length - self.wall_depth / 2.0, 0.0)])

        return walls

    def generate_wall_entity_parameters(self):

        for length, position in self.generate_external_wall_shapes():
            wall_params = self.config['wall'].copy()
            wall_params['width_length'] = [self.wall_depth*2, length]

            wall = Basic(initial_position=position, **wall_params)
            self.scene_entities.append(wall)

@SceneGenerator.register_subclass('room')
class Room(Scene):

    def __init__(self, custom_config):

        self.scene_type = 'room'

        __location__ = os.path.realpath(os.path.join(os.getcwd(), os.path.dirname(__file__)))
        with open(os.path.join(__location__, 'scene_layout_default.yml'), 'r') as yaml_file:
            default_config = yaml.load(yaml_file)[self.scene_type]

        custom_config = {**default_config, **custom_config}
        custom_config['scene_shape'] = custom_config[ 'room_shape' ]

        super(Room, self).__init__(custom_config)

        self.generate_external_wall_shapes()
        self.generate_wall_entity_parameters()






        # self.areas = [[self.width/2.0, self.length/2.0],
        #               [self.width - self.walls_depth, self.length - self.walls_depth]]

#
# @SceneGenerator.register_subclass('linear_rooms')
# class LinearRooms(Basic):
#
#     def __init__(self, params):
#         self.params = {**linear_rooms_scene_default, **params}
#
#         self.doorstep_type = self.params['doorstep_type']
#         self.doorstep_size = self.params['doorstep_size']
#
#         self.n_rooms = self.params['number_rooms']
#
#         self.width_room, self.length_room = self.params[ 'room_shape' ]
#         self.params['scene_shape'] = [ self.width_room, self.n_rooms * self.length_room ]
#
#         super(LinearRooms, self).__init__(self.params)
#
#         self.generate_external_wall_shapes()
#         self.generate_wall_entity_parameters()
#
#         self.positions_doorsteps = []
#
#         self.internal_walls_shapes = []
#
#         for n in range(self.n_rooms - 1):
#
#             pos_doorstep = self.generate_doorstep( y_coordinate = self.length * (n+1) / float(self.n_rooms) )
#
#             center = ( (self.width_room/2.0, self.length_room * n / 2.0))
#             shape = (self.width - self.walls_depth , self.length - self.walls_depth)
#
#             self.areas.append( (center, shape ) )
#             self.positions_doorsteps.append( pos_doorstep )
#
#         self.generate_internal_walls_entity_parameters()
#
#     def generate_doorstep(self, y_coordinate):
#
#         if self.doorstep_type == 'random':
#             position_doorstep = [y_coordinate,
#                                       random.uniform(self.doorstep_size / 2, self.width - self.doorstep_size / 2)]
#
#         elif self.doorstep_type == 'middle':
#             position_doorstep = [y_coordinate, self.width/ 2.0]
#
#
#         else:
#             raise ValueError( 'Doorstep type not implemented ')
#
#         #TODO: check rounding errors
#         right_wall = [(self.walls_depth, position_doorstep[1] - self.doorstep_size / 2),
#                       (y_coordinate, ((position_doorstep[1] - self.doorstep_size / 2) / 2.0), 0)]
#
#         coord_center_wall_left =  position_doorstep[1] + self.doorstep_size / 2 + (self.width - (position_doorstep[1] + self.doorstep_size / 2))/2.0
#         left_wall = [(self.walls_depth, self.width - (position_doorstep[1] + self.doorstep_size / 2)),
#                       (y_coordinate ,coord_center_wall_left, 0)]
#
#         self.internal_walls_shapes.append(left_wall)
#         self.internal_walls_shapes.append(right_wall)
#
#         return position_doorstep
#
#
#
#     def generate_internal_walls_entity_parameters(self):
#
#         internal_walls_texture = {
#             'type': 'random_tiles',
#             'min': [0, 140, 200],
#             'max': [0, 160, 250],
#             'size_tiles': 4
#         }
#
#         wall = {
#             'entity_type': 'basic',
#             'physical_shape': 'rectangle',
#             'movable': False,
#
#         }
#
#         for wall_shape in self.internal_walls_shapes:
#             depth_length, position = wall_shape
#             wall['shape_rectangle'] = depth_length
#             wall['position'] = position
#             wall['texture'] = internal_walls_texture
#
#             self.entity_parameters.append(wall.copy())
#
#
# @SceneGenerator.register_subclass('array_rooms')
# class ArrayRooms(Basic):
#
#     def __init__(self, params):
#         self.params = {**linear_rooms_scene_default, **params}
#
#         self.doorstep_type = self.params['doorstep_type']
#         self.doorstep_size = self.params['doorstep_size']
#
#         self.number_x_rooms, self.number_y_rooms = self.params['layout_rooms']
#
#         self.width_room, self.length_room = self.params[ 'room_shape' ]
#         self.params['scene_shape'] = [ self.x_rooms * self.width_room, self.y_rooms * self.length_room ]
#
#         super(ArrayRooms, self).__init__(self.params)
#
#         self.generate_external_wall_shapes()
#         self.generate_wall_entity_parameters()
#
#         # positions doorstep are matrix of trnsition from one room to another
#         self.positions_doorsteps = np.zeros((self.number_x_rooms * self.number_y_rooms, self.number_x_rooms * self.number_y_rooms, 3))
#         self.areas = np.zeros((self.number_x_rooms , self.number_y_rooms, 4))
#
#         self.internal_walls_shapes = []
#
#         for m in range(self.x_rooms ):
#             for n in range(self.y_rooms ):
#
#                 # horizontal doorstep
#                 if n != self.y_rooms - 1 :
#                     pos_doorstep_1 = self.generate_doorstep( x_coordinate = self.width_room * (m+0.5) ,
#                                                             y_coordinate = self.length_room * (n+1),
#                                                             orientation = 'horizontal' )
#
#                     self.positions_doorsteps[ n*m, (n+1)*m, : ] = pos_doorstep_1
#
#                 if m != self.x_rooms - 1 :
#                     pos_doorstep_2 = self.generate_horizontal_doorstep(x_coordinate=self.width_room * (m+1),
#                                                                    y_coordinate=self.length_room * (n+0.5),
#                                                                     orientation = 'vertical')
#
#                     self.positions_doorsteps[n * m, n * (m+1)] = pos_doorstep_2
#
#                 center = [self.width_room*(m +0.5) / 2.0 , self.length_room *(n +0.5) / 2.0 ]
#                 shape = [ self.width_room - self.walls_depth, self.length_room - self.walls_depth ]
#
#                 self.areas[m,n, :] = center + shape
#
#         self.generate_internal_walls_entity_parameters()
#
#     def generate_doorstep(self, x_coordinate, y_coordinate, orientation):
#
#         if self.doorstep_type == 'random':
#
#             if orientation == 'horizontal':
#
#                 position_doorstep = [y_coordinate,
#                                       random.uniform(x_coordinate + self.doorstep_size / 2, x_coordinate + self.width_room - self.doorstep_size / 2)]
#
#                 right_wall = [(self.walls_depth, position_doorstep[1] - self.doorstep_size / 2),
#                               (y_coordinate, ((position_doorstep[1] - self.doorstep_size / 2) / 2.0), 0)]
#
#                 coord_center_wall_left = position_doorstep[1] + self.doorstep_size / 2 + (
#                             self.width - (position_doorstep[1] + self.doorstep_size / 2)) / 2.0
#
#                 left_wall = [(self.walls_depth, self.width - (position_doorstep[1] + self.doorstep_size / 2)),
#                              (y_coordinate, coord_center_wall_left, 0)]
#
#
#             elif orientation == 'vertical':
#
#                 position_doorstep = [random.uniform(y_coordinate + self.doorstep_size / 2,
#                                                     y_coordinate + self.length_room - self.doorstep_size / 2),
#                                      x_coordinate,
#                                      ]
#
#
#             else:
#                 raise ValueError
#
#         elif self.doorstep_type == 'middle':
#             position_doorstep = [y_coordinate, x_coordinate]
#
#
#         else:
#             raise ValueError( 'Doorstep type not implemented ')
#
#         #TODO: check rounding errors
#
#         self.internal_walls_shapes.append(left_wall)
#         self.internal_walls_shapes.append(right_wall)
#
#         return position_doorstep
#
#     def generate_internal_walls_entity_parameters(self):
#
#         wall = {
#             'entity_type': 'basic',
#             'physical_shape': 'rectangle',
#             'movable': False,
#
#         }
#
#         for wall_shape in self.internal_walls_shapes:
#             depth_length, position = wall_shape
#             wall['shape_rectangle'] = depth_length
#             wall['position'] = position
#             wall['texture'] = self.walls_texture
#
#             self.entity_parameters.append(wall.copy())
