from flatland.playgrounds.playground import PlaygroundGenerator, Playground
from flatland.entities.basic import Basic
from flatland.entities.interactive import Door

import math, random


class ConnectedRooms2D(Playground):

    def __init__(self, size=(400, 200), n_rooms=(3,2), wall_type = 'classic', **kwargs):

        self.width, self.length = size

        default_config = self.parse_configuration('empty', 'connected-rooms-2d')
        playground_params = {**default_config, **kwargs}

        if 'wall_texture' in kwargs:
            self.wall_texture = kwargs['wall_texture']
        else:
            self.wall_texture = self.parse_configuration('empty', wall_type)

        default_wall_params = self.parse_configuration('empty', 'wall')
        if 'wall_params' in kwargs:
            self.wall_params = {**default_wall_params, **kwargs['wall_params']}
        else:
            self.wall_params = default_wall_params


        self.wall_params['texture'] = self.wall_texture
        self.wall_depth = self.wall_params['depth']


        self.doorstep_type = playground_params['doorstep_type']
        self.doorstep_size = playground_params['doorstep_size']

        self.size_door = [self.wall_depth, self.doorstep_size]

        self.n_rooms = n_rooms
        self.width_room = float(self.width)/self.n_rooms[0]
        self.length_room = float(self.length)/self.n_rooms[1]

        self.area_rooms = self.compute_area_rooms()
        self.doorsteps = self.compute_doorsteps()

        room_wall_entities = self.generate_doorstep_wall_entities()

        wall_lenths_and_positions = self.generate_external_wall_lengths_and_positions()
        external_wall_entities = self.generate_external_wall_entities(wall_lenths_and_positions)

        all_walls = room_wall_entities + external_wall_entities
        if hasattr(self, 'scene_entities'):
            self.scene_entities = self.scene_entities + all_walls
        else:
            self.scene_entities = all_walls

        super(ConnectedRooms2D, self).__init__(size=size, wall_type = wall_type, **playground_params)



    def compute_area_rooms(self):

        areas = {}

        for n in range(self.n_rooms[0]):
            for m in range(self.n_rooms[1]):

                x_center = self.width_room/2.0 + n * self.width_room
                y_center = self.length_room/2.0 + m * self.length_room

                center = (x_center, y_center)
                shape = (self.width_room-self.wall_depth, self.length_room-self.wall_depth)

                areas[(n, m)] = (center, shape )

        return areas

    def compute_doorsteps(self):

        doorsteps = {}

        room_transitions = []
        for n in range(self.n_rooms[0]):
            for m in range(self.n_rooms[1]):

                if n != self.n_rooms[0]-1:
                    room_transitions.append( ( (n,m), (n+1,m), 'vertical') )

                if m != self.n_rooms[1]-1:
                    room_transitions.append( ( (n,m), (n,m+1), 'horizontal') )


        for room_1_index, room_2_index, orientation in room_transitions:

            # Orientation corresponds to orientation of the doorstep
            center_room_1 = self.area_rooms[room_1_index][0]
            center_room_2 = self.area_rooms[room_2_index][0]

            x_doorstep = (center_room_1[0] + center_room_2[0]) / 2
            y_doorstep = (center_room_1[1] + center_room_2[1]) / 2

            # Calculate center doorstep in the case where doorstep is not random
            if self.doorstep_type == 'random':

                if orientation is 'horizontal':

                    left = center_room_1[0] - self.width_room/2.0
                    right = center_room_1[0] + self.width_room/2.0
                    x_doorstep = random.uniform(left + self.doorstep_size / 2, right - self.doorstep_size / 2)

                else:

                    down = center_room_1[1] - self.length_room/2.0
                    up = center_room_1[1] + self.length_room/2.0
                    y_doorstep = random.uniform(down + self.doorstep_size / 2, up - self.doorstep_size / 2)

            elif self.doorstep_type == 'middle':
                pass

            else:
                raise ValueError('doorstep not implemented')

            doorsteps[(room_1_index, room_2_index)] = (x_doorstep, y_doorstep, orientation)

        return doorsteps

    def generate_doorstep_wall_entities(self):

        walls = []

        for _, doorstep_coordinates in self.doorsteps.items():

            x, y, orientation = doorstep_coordinates

            if orientation is 'vertical':
                lower_wall_length = (y%self.length_room) - self.doorstep_size / 2.0
                upper_wall_length = self.length_room - (y%self.length_room + self.doorstep_size / 2.0)

                # size, center
                lower_wall_position = (x, y - self.doorstep_size / 2.0 - lower_wall_length / 2.0, math.pi/2 )
                upper_wall_position = (x, y + self.doorstep_size / 2.0 + upper_wall_length/2.0, math.pi/2 )

                lower_wall = Basic(initial_position=lower_wall_position, width_length=[self.wall_depth , lower_wall_length],
                                   **self.wall_params)
                upper_wall = Basic(initial_position=upper_wall_position, width_length=[self.wall_depth , upper_wall_length],
                                   **self.wall_params)

                walls.append(lower_wall)
                walls.append(upper_wall)

            else:
                left_wall_length = (x % self.width_room) - self.doorstep_size / 2.0
                right_wall_length = self.width_room - (x % self.width_room + self.doorstep_size / 2.0)

                # size, center
                left_wall_position = ( x - self.doorstep_size / 2.0 - left_wall_length / 2.0, y, 0)
                right_wall_position = ( x + self.doorstep_size / 2.0 + right_wall_length / 2.0, y, 0)

                left_wall = Basic(initial_position=left_wall_position,
                                   width_length=[self.wall_depth, left_wall_length],
                                   **self.wall_params)
                right_wall = Basic(initial_position=right_wall_position,
                                   width_length=[self.wall_depth, right_wall_length],
                                   **self.wall_params)

                walls.append(left_wall)
                walls.append(right_wall)


        return walls

    def generate_external_wall_lengths_and_positions(self):
        """
        Generate list of (length, (position x, position y, theta)) for walls around the scene

        :return:
        """
        walls = []

        walls.append([ self.length, (0, self.length / 2.0, math.pi / 2.0)])
        walls.append([ self.length, (self.width , self.length / 2.0,  math.pi / 2.0)])
        walls.append([ self.width, ( self.width / 2.0, 0, 0.0)])
        walls.append([ self.width, ( self.width / 2.0, self.length , 0.0)])

        return walls

    def generate_external_wall_entities(self, wall_lengths_and_positions):

        wall_entities = []

        for length, position in wall_lengths_and_positions:
            wall_params = self.wall_params.copy()
            wall_params['width_length'] = [self.wall_depth*2, length]

            wall = Basic(initial_position=position, **wall_params)
            wall_entities.append(wall)

        return wall_entities

    def add_door(self, doorstep):

        x, y, orientation = doorstep
        if orientation == 'horizontal':
            theta = 0
        else:
            theta = math.pi/2

        door = Door([x,y,theta], width_length = [self.wall_depth, self.doorstep_size])

        self.add_entity(door)

        return door

    def random_position_on_wall(self, area_coordinates, wall_location, size_object):

        area_center, area_size = self.area_rooms[area_coordinates]

        if wall_location == 'up':
            y = area_center[1] + area_size[1]/2

        elif wall_location == 'down':
            y = area_center[1] - area_size[1] / 2

        elif wall_location == 'left':
            x = area_center[0] - area_size[0] / 2

        elif wall_location == 'right':
            x = area_center[0] + area_size[0] / 2

        else:
            raise ValueError

        while (True):

            if wall_location in ['up', 'down']:

                x = random.uniform(area_center[0] - area_size[0] / 2, area_center[0] + area_size[0] / 2)

            elif wall_location in ['left', 'right']:

                y = random.uniform(area_center[1] - area_size[1] / 2, area_center[1] + area_size[1] / 2)

            else:
                raise ValueError

            close_to_doorstep = False

            for _, doorstep in self.doorsteps.items():
                if ((doorstep[0] - x) ** 2 + (doorstep[1] - y)**2 ) < size_object ** 2:
                    close_to_doorstep = True

            if not close_to_doorstep:
                break

        return x,y

    def get_quarter_area(self, area_coordinates, area_location):

        area_center, area_size = self.area_rooms[area_coordinates]

        if area_location == 'up-left':
            center = area_center[0] - area_size[0] / 4, area_center[1] + area_size[1] / 4
        elif area_location == 'up-right':
            center = area_center[0] + area_size[0] / 4, area_center[1] + area_size[1] / 4
        elif area_location == 'down-left':
            center = area_center[0] - area_size[0] / 4, area_center[1] - area_size[1] / 4
        elif area_location == 'down-right':
            center = area_center[0] + area_size[0] / 4, area_center[1] - area_size[1] / 4
        else:
            raise ValueError

        quarter_area_size = [area_size[0]/2, area_size[1]/2]

        return center, quarter_area_size

class SingleRoom(ConnectedRooms2D):

    def __init__(self, size = (200, 200), wall_type = 'classic', **kwargs):

        super(SingleRoom, self).__init__( size=size, n_rooms=(1,1), wall_type = wall_type, **kwargs)


class LinearRooms(ConnectedRooms2D):

    def __init__(self, size = (200, 200), n_rooms = 3, wall_type = 'classic', **kwargs):

        super(LinearRooms, self).__init__( size=size, n_rooms=(n_rooms,1), wall_type = wall_type, **kwargs)