"""
Empty Playgrounds with built-in walls and rooms

"""

import math
import random

from simple_playgrounds.playgrounds.playground import Playground
from simple_playgrounds.entities.scene_elements import Basic, Door

#pylint: disable=line-too-long

class ConnectedRooms2D(Playground):

    """
    Multiple rooms with a grid layout
    """

    def __init__(self, size=(400, 200), n_rooms=(3, 2), wall_type='classic', **kwargs):

        self.width, self.length = size

        default_config = self.parse_configuration('connected-rooms-2d')
        playground_params = {**default_config, **kwargs}

        self.wall_texture = kwargs.get('wall_texture', self.parse_configuration(wall_type))

        self.wall_params = {**self.parse_configuration('wall'), **kwargs.get('wall_params', {})}
        self.wall_params['texture'] = self.wall_texture
        self.wall_depth = self.wall_params['depth']

        self.doorstep_type = playground_params['doorstep_type']
        self.doorstep_size = playground_params['doorstep_size']

        self.size_door = [self.wall_depth, self.doorstep_size]

        self.n_rooms = n_rooms
        self.width_room = float(self.width)/self.n_rooms[0]
        self.length_room = float(self.length)/self.n_rooms[1]

        self.area_rooms = self._compute_area_rooms()
        self.doorsteps = self._compute_doorsteps()

        room_wall_entities = self._generate_doorstep_wall_entities()

        wall_lengths_and_positions = self._generate_external_wall_lengths_and_positions()
        external_wall_entities = self._generate_external_wall_entities(wall_lengths_and_positions)

        all_walls = room_wall_entities + external_wall_entities
        if hasattr(self, 'scene_entities'):
            self.scene_entities = self.scene_entities + all_walls
        else:
            self.scene_entities = all_walls

        super(ConnectedRooms2D, self).__init__(size=size)

    def _compute_area_rooms(self):

        areas = {}

        for n_width in range(self.n_rooms[0]):
            for n_length in range(self.n_rooms[1]):

                x_center = self.width_room/2.0 + n_width * self.width_room
                y_center = self.length_room/2.0 + n_length * self.length_room

                center = (x_center, y_center)
                shape = (self.width_room-self.wall_depth, self.length_room-self.wall_depth)

                areas[(n_width, n_length)] = (center, shape)

        return areas

    def _compute_doorsteps(self):

        doorsteps = {}

        room_transitions = []
        for n_width in range(self.n_rooms[0]):
            for n_length in range(self.n_rooms[1]):

                if n_width != self.n_rooms[0]-1:
                    room_transitions.append(((n_width, n_length), (n_width+1, n_length), 'vertical'))

                if n_length != self.n_rooms[1]-1:
                    room_transitions.append(((n_width, n_length), (n_width, n_length+1), 'horizontal'))

        for room_1_index, room_2_index, orientation in room_transitions:

            # Orientation corresponds to orientation of the doorstep
            center_room_1 = self.area_rooms[room_1_index][0]
            center_room_2 = self.area_rooms[room_2_index][0]

            x_doorstep = (center_room_1[0] + center_room_2[0]) / 2
            y_doorstep = (center_room_1[1] + center_room_2[1]) / 2

            # Calculate center doorstep in the case where doorstep is not random
            if self.doorstep_type == 'random':

                if orientation == 'horizontal':

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

    def _generate_doorstep_wall_entities(self):

        walls = []

        for _, doorstep_coordinates in self.doorsteps.items():

            pos_x, pos_y, orientation = doorstep_coordinates

            if orientation == 'vertical':
                lower_wall_length = (pos_y%self.length_room) - self.doorstep_size / 2.0
                upper_wall_length = self.length_room - (pos_y%self.length_room + self.doorstep_size / 2.0)

                # size, center
                lower_wall_position = (pos_x, pos_y - self.doorstep_size / 2.0 - lower_wall_length / 2.0, math.pi/2)
                upper_wall_position = (pos_x, pos_y + self.doorstep_size / 2.0 + upper_wall_length/2.0, math.pi/2)

                lower_wall = Basic(initial_position=lower_wall_position, width_length=[self.wall_depth, lower_wall_length],
                                   **self.wall_params)
                upper_wall = Basic(initial_position=upper_wall_position, width_length=[self.wall_depth, upper_wall_length],
                                   **self.wall_params)

                walls.append(lower_wall)
                walls.append(upper_wall)

            else:
                left_wall_length = (pos_x % self.width_room) - self.doorstep_size / 2.0
                right_wall_length = self.width_room - (pos_x % self.width_room + self.doorstep_size / 2.0)

                # size, center
                left_wall_position = (pos_x - self.doorstep_size / 2.0 - left_wall_length / 2.0, pos_y, 0)
                right_wall_position = (pos_x + self.doorstep_size / 2.0 + right_wall_length / 2.0, pos_y, 0)

                left_wall = Basic(initial_position=left_wall_position,
                                  width_length=[self.wall_depth, left_wall_length],
                                  **self.wall_params)
                right_wall = Basic(initial_position=right_wall_position,
                                   width_length=[self.wall_depth, right_wall_length],
                                   **self.wall_params)

                walls.append(left_wall)
                walls.append(right_wall)

        return walls

    def _generate_external_wall_lengths_and_positions(self):

        walls = []

        for vert in range(self.n_rooms[1]):
            walls.append([self.length_room, (0, vert * self.length_room + self.length_room / 2.0, math.pi / 2.0)])
            walls.append([self.length_room, (self.width, vert * self.length_room + self.length_room / 2.0, math.pi / 2.0)])

        for hor in range(self.n_rooms[0]):
            walls.append([self.width_room, (hor * self.width_room + self.width_room / 2.0, 0, 0)])
            walls.append([self.width_room, (hor * self.width_room + self.width_room / 2.0, self.length, 0)])


        # walls = [[self.length, (0, self.length / 2.0, math.pi / 2.0)],
        #          [self.length, (self.width, self.length / 2.0, math.pi / 2.0)],
        #          [self.width, (self.width / 2.0, 0, 0.0)],
        #          [self.width, (self.width / 2.0, self.length, 0.0)]]

        return walls

    def _generate_external_wall_entities(self, wall_lengths_and_positions):

        wall_entities = []

        for length, position in wall_lengths_and_positions:
            wall_params = self.wall_params.copy()
            wall_params['width_length'] = [self.wall_depth*2, length]

            wall = Basic(initial_position=position, **wall_params)
            wall_entities.append(wall)

        return wall_entities

    def add_door(self, doorstep):
        """ Add a door to the Playground, at a particular doostep

        Args:
            doorstep: coordinates of the doorstep

        Returns:
            Scene Element Door
        """

        pos_x, pos_y, orientation = self.doorsteps[doorstep]

        if orientation == 'horizontal':
            theta = 0
        else:
            theta = math.pi/2

        door = Door([pos_x, pos_y, theta], width_length=[self.wall_depth, self.doorstep_size])

        self.add_scene_element(door)

        return door

    def random_position_on_wall(self, area_coordinates, wall_location, size_object):

        """

        Finds a random position on a particular wall.
        Used to place a switch.

        Args:
            area_coordinates: coordinates of the room
            wall_location: up, down, left or right
            size_object: size of the scene element to add to the wall.

        Returns:

        """

        area_center, area_size = self.area_rooms[area_coordinates]

        pos_x, pos_y = 0, 0

        if wall_location == 'up':
            pos_y = area_center[1] + area_size[1]/2

        elif wall_location == 'down':
            pos_y = area_center[1] - area_size[1] / 2

        elif wall_location == 'left':
            pos_x = area_center[0] - area_size[0] / 2

        elif wall_location == 'right':
            pos_x = area_center[0] + area_size[0] / 2

        else:
            raise ValueError

        while True:

            if wall_location in ['up', 'down']:

                pos_x = random.uniform(area_center[0] - area_size[0] / 2, area_center[0] + area_size[0] / 2)

            elif wall_location in ['left', 'right']:

                pos_y = random.uniform(area_center[1] - area_size[1] / 2, area_center[1] + area_size[1] / 2)

            else:
                raise ValueError

            close_to_doorstep = False

            for _, doorstep in self.doorsteps.items():
                if ((doorstep[0] - pos_x) ** 2 + (doorstep[1] - pos_y)**2) < size_object ** 2:
                    close_to_doorstep = True

            if not close_to_doorstep:
                break

        return pos_x, pos_y, 0

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

    """
    Playground composed of a single room
    """

    def __init__(self, size=(200, 200), wall_type='classic', **kwargs):

        super(SingleRoom, self).__init__(size=size, n_rooms=(1, 1), wall_type=wall_type, **kwargs)


class LinearRooms(ConnectedRooms2D):
    """
    Playground composed of connected rooms organized as a line
    """

    def __init__(self, size=(200, 200), n_rooms=3, wall_type='classic', **kwargs):

        super(LinearRooms, self).__init__(size=size, n_rooms=(n_rooms, 1), wall_type=wall_type, **kwargs)
