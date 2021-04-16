"""
Empty Playgrounds with built-in walls and rooms

"""
from typing import Union, Dict, Tuple

from collections import namedtuple

import math
import random
import numpy as np

from simple_playgrounds.playground import Playground
from simple_playgrounds.utils.texture import TextureGenerator, Texture
from simple_playgrounds.elements.elements.basic import Wall, Door
from simple_playgrounds.utils.position_utils import CoordinateSampler
from simple_playgrounds.utils.parser import parse_configuration


Room = namedtuple('Room', ['center', 'width', 'length', 'r', 'c', 'index'])


class ConnectedRooms2D(Playground):
    """
    Multiple rooms with a grid layout.
    Rooms counted top to bottom, left to right, .
    Rooms in row, column numpy style.
    """

    def __init__(self,
                 size: Tuple[int, int],
                 room_layout: Tuple[int, int],
                 doorstep_size: int,
                 doorstep_type: str = 'middle',
                 wall_type='classic',
                 wall_depth=10,
                 wall_texture_seed: Union[int, None] = None,
                 **wall_params,
                 ):
        """

        Args:
            size:
            room_layout:
            doorstep_size:
            doorstep_type:
            wall_type:
            wall_texture_seed:
            **wall_params:


        Wall parameters take priority on wall type.

        """

        # Playground Layout

        super().__init__(size=size)

        self._doorstep_type = doorstep_type
        self._doorstep_size = doorstep_size

        self._size_door = (wall_depth, self._doorstep_size)

        self._room_layout = room_layout
        self.rooms = self._compute_rooms()
        self.doorsteps = self._compute_doorsteps()

        # Wall parameters
        rng_texture = np.random.default_rng(wall_texture_seed)

        wall_type_params = parse_configuration('playground', wall_type)
        wall_params = {**wall_type_params,
                       **wall_params,
                       'rng': rng_texture}
        self._wall_params = wall_params
        self._wall_depth = wall_depth

        # Set random texture for possible replication
        self._add_external_walls()
        # self._add_room_walls()

        # By default, an agent starts in a random position of the first room
        first_room = self.rooms[0]
        center, size = first_room.center, (first_room.width, first_room.length)
        self.initial_agent_coordinates = CoordinateSampler(center=center,
                                                           area_shape='rectangle',
                                                           width_length=size)

    def _compute_rooms(self):

        rooms = []
        width_room = int(self.size[0] / self._room_layout[1])
        length_room = int(self.size[1] / self._room_layout[0])

        index = 0

        for r in range(self._room_layout[0]):
            for c in range(self._room_layout[1]):

                x_center = width_room / 2.0 + c * width_room
                y_center = length_room / 2.0 + r * length_room

                center = (x_center, y_center)

                room = Room(center=center, index=index, width=width_room, length=length_room, r=r, c=c)
                rooms.append(room)
                index += 1

        return rooms

    def _add_external_walls(self):

        upper_rooms = [room for room in self.rooms if room.r == 0]
        lower_rooms = [room for room in self.rooms if room.r == self._room_layout[0] - 1]
        left_rooms = [room for room in self.rooms if room.c == 0]
        right_rooms = [room for room in self.rooms if room.c == self._room_layout[1] - 1]

        for room in upper_rooms:

            # Horizontal walls
            size_wall = (self._wall_depth * 2, room.width)
            texture = {**self._wall_params, 'size': size_wall}
            wall = Wall(size=size_wall, texture=texture)
            coord = (room.center[0], room.center[1] - room.length/2), 0
            self.add_element(wall, coord)

        for room in lower_rooms:

            # Horizontal walls
            size_wall = (self._wall_depth * 2, room.width)
            texture = {**self._wall_params, 'size': size_wall}
            wall = Wall(size=size_wall, texture=texture)
            coord = (room.center[0], room.center[1] + room.length/2), 0
            self.add_element(wall, coord)

        for room in right_rooms:

            # Horizontal walls
            size_wall = (self._wall_depth * 2, room.length)
            texture = {**self._wall_params, 'size': size_wall}
            wall = Wall(size=size_wall, texture=texture)
            coord = (room.center[0], room.center[1] + room.width/2), math.pi/2
            self.add_element(wall, coord)

        for room in left_rooms:

            # Horizontal walls
            size_wall = (self._wall_depth * 2, room.length)
            texture = {**self._wall_params, 'size': size_wall}
            wall = Wall(size=size_wall, texture=texture)
            coord = (room.center[0], room.center[1] - room.width/2), math.pi/2
            self.add_element(wall, coord)


    def _compute_doorsteps(self):

        doorsteps = {}

        room_transitions = []
        for n_width in range(self.room_layout[0]):
            for n_length in range(self.room_layout[1]):

                if n_width != self.room_layout[0]-1:
                    room_transitions.append(((n_width, n_length), (n_width+1, n_length),
                                             'vertical'))

                if n_length != self.room_layout[1]-1:
                    room_transitions.append(((n_width, n_length), (n_width, n_length+1),
                                             'horizontal'))

        for room_1_index, room_2_index, orientation in room_transitions:

            # Orientation corresponds to orientation of the doorstep
            center_room_1 = self.area_rooms[room_1_index][0]
            center_room_2 = self.area_rooms[room_2_index][0]

            x_doorstep = (center_room_1[0] + center_room_2[0]) / 2
            y_doorstep = (center_room_1[1] + center_room_2[1]) / 2

            # Calculate center doorstep in the case where doorstep is not random
            if self._doorstep_type == 'random':

                if orientation == 'horizontal':

                    left = center_room_1[0] - self._width_room / 2.0 + self._doorstep_size / 2
                    right = center_room_1[0] + self._width_room / 2.0 - self._doorstep_size / 2
                    x_doorstep = random.uniform(left, right)

                else:

                    down = center_room_1[1] - self._length_room / 2.0 + self._doorstep_size / 2
                    up = center_room_1[1] + self._length_room / 2.0 - self._doorstep_size / 2
                    y_doorstep = random.uniform(down, up)

            elif self._doorstep_type == 'middle':
                pass

            else:
                raise ValueError('doorstep not implemented')

            doorsteps[(room_1_index, room_2_index)] = ((x_doorstep, y_doorstep), orientation)

        return doorsteps

    def _add_room_walls(self):

        for _, doorstep_coordinates in self.doorsteps.items():

            (pos_x, pos_y), orientation = doorstep_coordinates

            if orientation == 'vertical':
                lower_wall_length = (pos_y % self._length_room) - self._doorstep_size / 2.0
                upper_wall_length = self._length_room \
                                    - (pos_y % self._length_room + self._doorstep_size / 2.0)

                # size, center
                lower_wall_position = ((pos_x,
                                       pos_y - self._doorstep_size / 2.0 - lower_wall_length / 2.0),
                                       math.pi / 2)
                upper_wall_position = ((pos_x,
                                       pos_y + self._doorstep_size / 2.0 + upper_wall_length / 2.0),
                                       math.pi / 2)

                lower_wall = Wall(size=[self._wall_depth, lower_wall_length],
                                   **self._wall_params)
                upper_wall = Wall(size=[self._wall_depth, upper_wall_length],
                                   **self._wall_params)

                self.add_element(lower_wall, lower_wall_position)
                self.add_element(upper_wall, upper_wall_position)

            else:
                left_wall_length = (pos_x % self._width_room) - self._doorstep_size / 2.0
                right_wall_length = self._width_room\
                                    - (pos_x % self._width_room + self._doorstep_size / 2.0)

                # size, center
                left_wall_position = ((pos_x - self._doorstep_size / 2.0 - left_wall_length / 2.0,
                                      pos_y),
                                      0)
                right_wall_position = ((pos_x + self._doorstep_size / 2.0 + right_wall_length / 2.0,
                                       pos_y),
                                       0)

                left_wall = Wall(size=[self._wall_depth, left_wall_length],
                                 **self._wall_params,
                                 )
                right_wall = Wall(size=[self._wall_depth, right_wall_length],
                                  **self._wall_params)

                self.add_element(left_wall, left_wall_position)
                self.add_element(right_wall, right_wall_position)



    def add_door(self, doorstep):
        """ Add a door to the Playground, at a particular doostep

        Args:
            doorstep: coordinates of the doorstep

        Returns:
            Scene Element Door
        """

        (pos_x, pos_y), orientation = self.doorsteps[doorstep]

        if orientation == 'horizontal':
            theta = 0
        else:
            theta = math.pi/2

        door = Door(width_length=[self._wall_depth, self._doorstep_size])

        self.add_element(door, ((pos_x, pos_y), theta))

        return door

    def random_position_on_wall(self, area_coordinates, wall_location, radius_object):

        """

        Finds a random position on a particular wall.
        Used to place a switch.

        Args:
            area_coordinates: coordinates of the room
            wall_location: up, down, left or right
            radius_object: size of the scene element to add to the wall.

        Returns:

        """

        area_center, area_size = self.area_rooms[area_coordinates]

        pos_x, pos_y = 0, 0

        if wall_location == 'up':
            pos_y = area_center[1] - area_size[1]/2

        elif wall_location == 'down':
            pos_y = area_center[1] + area_size[1] / 2

        elif wall_location == 'left':
            pos_x = area_center[0] - area_size[0] / 2

        elif wall_location == 'right':
            pos_x = area_center[0] + area_size[0] / 2

        else:
            raise ValueError

        while True:

            if wall_location in ['up', 'down']:

                pos_x = random.uniform(area_center[0] - area_size[0] / 2,
                                       area_center[0] + area_size[0] / 2)

            elif wall_location in ['left', 'right']:

                pos_y = random.uniform(area_center[1] - area_size[1] / 2,
                                       area_center[1] + area_size[1] / 2)

            close_to_doorstep = False

            for _, doorstep in self.doorsteps.items():
                (doorstep_x, doorstep_y), _ = doorstep
                if ((doorstep_x - pos_x) ** 2 + (doorstep_y - pos_y)**2)\
                        < ((radius_object + self._doorstep_size) / 2) ** 2:
                    close_to_doorstep = True

            if not close_to_doorstep:
                break

        return (pos_x, pos_y), 0

    def get_area(self, room_coordinates, area_location):
        """
        Get particular area in a room.
        
        Args:
            room_coordinates: coordinate of the room.
            area_location (str): can be 'up', 'down', 'right', 'left',
                                 'up-right', 'up-left', 'down-right', or 'down-left'

        Returns: center, size

        """

        area_center, area_size = self.area_rooms[room_coordinates]

        if area_location not in ['up', 'down', 'right', 'left',
                                 'up-right', 'up-left', 'down-right', 'down-left']:
            raise ValueError('area_location not correct')

        size_y = area_size[1] / 2
        if 'up' in area_location:
            center_y = area_center[1] - area_size[1] / 4
        elif 'down' in area_location:
            center_y = area_center[1] + area_size[1] / 4
        else:
            center_y = area_center[1]
            size_y = area_size[1]

        size_x = area_size[0] / 2
        if 'right' in area_location:
            center_x = area_center[0] + area_size[0] / 4
        elif 'left' in area_location:
            center_x = area_center[0] - area_size[0] / 4
        else:
            center_x = area_center[0]
            size_x = area_size[0]

        return [center_x, center_y], [size_x, size_y]


class SingleRoom(ConnectedRooms2D):

    """
    Playground composed of a single room
    """

    def __init__(self,
                 size,
                 wall_type='classic',
                 **kwargs):

        super().__init__(size=size, room_layout=(1, 1), wall_type=wall_type,
                         doorstep_size = 0,
                         **kwargs)

    def _compute_doorsteps(self):
        pass


class LinearRooms(ConnectedRooms2D):
    """
    Playground composed of connected rooms organized as a line
    """

    def __init__(self, size=(200, 200), room_layout=3, wall_type='classic', **kwargs):

        super().__init__(size=size, room_layout=(room_layout, 1), wall_type=wall_type, **kwargs)
