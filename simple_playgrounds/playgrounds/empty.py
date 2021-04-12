"""
Empty Playgrounds with built-in walls and rooms

"""

import math
import random
import numpy as np

from simple_playgrounds.playground import Playground
from simple_playgrounds.playgrounds.scene_elements import Wall, Door
from simple_playgrounds.utils.position_utils import CoordinateSampler
from simple_playgrounds.utils.parser import parse_configuration


class ConnectedRooms2D(Playground):
    """
    Multiple rooms with a grid layout
    """

    def __init__(self, size=(400, 200), room_layout=(3, 2), wall_type='classic',
                 wall_texture_seed=None,
                 **kwargs):

        self.width, self.length = size

        default_config = parse_configuration('playground', 'connected-rooms-2d')
        playground_params = {**default_config, **kwargs}

        # Wall parameters
        self.rng_texture = np.random.default_rng(wall_texture_seed)
        self._wall_texture = kwargs.get('wall_texture', parse_configuration('playground', wall_type))
        self._wall_texture['rng_texture'] = self.rng_texture
        self._wall_params = {**parse_configuration('playground', 'wall'), **kwargs.get('wall_params', {}),
                             'texture': self._wall_texture, }
        self._wall_depth = self._wall_params['depth']

        # Door parameters
        self._doorstep_type = playground_params['doorstep_type']
        self._doorstep_size = playground_params['doorstep_size']
        self._size_door = [self._wall_depth, self._doorstep_size]

        # Environment Layout
        self.room_layout = room_layout
        self._width_room = float(self.width) / self.room_layout[0]
        self._length_room = float(self.length) / self.room_layout[1]

        self.area_rooms = self._compute_area_rooms()
        self.doorsteps = self._compute_doorsteps()

        super().__init__(size=size)

        # Set random texture for possible replication
        self._add_external_walls()
        self._add_room_walls()

        # By default, an agent starts in a random position of the first room
        center, shape = self.area_rooms[(0, 0)]
        shape = shape[0] - self._wall_depth, shape[1] - self._wall_depth
        self.initial_agent_coordinates = CoordinateSampler(center=center,
                                                           area_shape='rectangle',
                                                           width_length=shape)

    def _compute_area_rooms(self):

        areas = {}

        for n_width in range(self.room_layout[0]):
            for n_length in range(self.room_layout[1]):

                x_center = self._width_room / 2.0 + n_width * self._width_room
                y_center = self._length_room / 2.0 + n_length * self._length_room

                center = (x_center, y_center)
                shape = (self._width_room - self._wall_depth, self._length_room - self._wall_depth)

                areas[(n_width, n_length)] = (center, shape)

        return areas

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

                lower_wall = Wall(width_length=[self._wall_depth, lower_wall_length],
                                   **self._wall_params)
                upper_wall = Wall(width_length=[self._wall_depth, upper_wall_length],
                                   **self._wall_params)

                self.add_scene_element(lower_wall, lower_wall_position)
                self.add_scene_element(upper_wall, upper_wall_position)

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

                left_wall = Wall(width_length=[self._wall_depth, left_wall_length],
                                 **self._wall_params,
                                 )
                right_wall = Wall(width_length=[self._wall_depth, right_wall_length],
                                  **self._wall_params)

                self.add_scene_element(left_wall, left_wall_position)
                self.add_scene_element(right_wall, right_wall_position)

    def _add_external_walls(self):

        wall_params = self._wall_params.copy()

        for vert in range(self.room_layout[1]):

            wall_params['width_length'] = [self._wall_depth * 2, self._length_room]

            wall = Wall(**wall_params)
            position = (0, vert * self._length_room + self._length_room / 2.0), math.pi / 2.0
            self.add_scene_element(wall, position)

            wall = Wall(**wall_params)
            position = (self.width, vert * self._length_room + self._length_room / 2.0), math.pi / 2.0
            self.add_scene_element(wall, position)

        for hor in range(self.room_layout[0]):

            wall_params['width_length'] = [self._wall_depth * 2, self._width_room]

            wall = Wall(**wall_params)
            position = (hor * self._width_room + self._width_room / 2.0, 0), 0
            self.add_scene_element(wall, position)

            wall = Wall(**wall_params)
            position = (hor * self._width_room + self._width_room / 2.0, self.length), 0
            self.add_scene_element(wall, position)

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

        self.add_scene_element(door, ((pos_x, pos_y), theta))

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

    def __init__(self, size=(200, 200), wall_type='classic', **kwargs):

        super().__init__(size=size, room_layout=(1, 1), wall_type=wall_type, **kwargs)


class LinearRooms(ConnectedRooms2D):
    """
    Playground composed of connected rooms organized as a line
    """

    def __init__(self, size=(200, 200), room_layout=3, wall_type='classic', **kwargs):

        super().__init__(size=size, room_layout=(room_layout, 1), wall_type=wall_type, **kwargs)
