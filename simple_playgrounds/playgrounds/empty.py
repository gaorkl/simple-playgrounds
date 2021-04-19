"""
Empty Playgrounds with built-in walls and rooms

"""
from typing import Union, Dict, Tuple

from collections import namedtuple

import math
import random
import numpy as np
import pymunk

from simple_playgrounds.playground import Playground
from simple_playgrounds.utils.texture import Texture
from simple_playgrounds.elements.elements.basic import Wall, Door
from simple_playgrounds.utils.position_utils import CoordinateSampler
from simple_playgrounds.utils.parser import parse_configuration

MIN_WALL_LENGTH = 20


class Doorstep:

    def __init__(self,
                 position,
                 size,
                 depth):

        self.position = position
        self.size = size
        self.depth = depth

        self._start_point = None
        self._end_point = None

    @property
    def start_point(self):
        return self._start_point

    @start_point.setter
    def start_point(self, pt):
        self._start_point = pt

    @property
    def end_point(self):
        return self._end_point

    @end_point.setter
    def end_point(self, pt):
        self._end_point = pt

    def generate_door(self, **door_params):

        door = Door(start_point=self.start_point, end_point=self.end_point,
                    door_depth = self.depth,
                    **door_params)

        return door


class RectangleRoom:

    def __init__(self,
                 center: Tuple[int, int],
                 size: Tuple[int, int],
                 wall_depth: int,
                 wall_texture_params: Union[Dict, Texture],
                 doorstep_up: Union[None, Doorstep] = None,
                 doorstep_down: Union[None, Doorstep] = None,
                 doorstep_left: Union[None, Doorstep] = None,
                 doorstep_right: Union[None, Doorstep] = None,
                 ):

        self.center = pymunk.Vec2d(*center)
        self.width, self.length = size
        self.size = size

        self._wall_depth = wall_depth
        self._wall_texture_params = wall_texture_params

        self.doorstep_up = doorstep_up
        self.doorstep_down = doorstep_down
        self.doorstep_left = doorstep_left
        self.doorstep_right = doorstep_right

        self._doors = {}

    def generate_walls(self):

        # UP walls
        start = self.center + (-self.width / 2, -self.length / 2)
        end = self.center + (self.width / 2, -self.length / 2)
        for wall in self._generate_wall(start, end, self.doorstep_up):
            yield wall

        # DOWN WALLS
        start = self.center + (-self.width / 2, self.length / 2)
        end = self.center + (self.width / 2, self.length / 2)
        for wall in self._generate_wall(start, end, self.doorstep_down):
            yield wall

        # LEFT WALLS
        start = self.center + (-self.width / 2, -self.length / 2)
        end = self.center + (-self.width / 2, self.length / 2)
        for wall in self._generate_wall(start, end, self.doorstep_left):
            yield wall

        # RIGHT WALLS
        start = self.center + (self.width / 2, -self.length / 2)
        end = self.center + (self.width / 2, self.length / 2)
        for wall in self._generate_wall(start, end, self.doorstep_right):
            yield wall

    def _generate_wall(self,
                       start: pymunk.Vec2d,
                       end: pymunk.Vec2d,
                       doorstep: Doorstep):

        if doorstep:
            assert isinstance(doorstep, Doorstep)

            middle_left = start + (end-start).normalized() * (doorstep.position - doorstep.size/2)
            wall = Wall(start, middle_left, wall_depth=self._wall_depth, texture=self._wall_texture_params)

            yield wall

            middle_right = start + (end-start).normalized() * (doorstep.position + doorstep.size/2)
            wall = Wall(middle_right, end, wall_depth=self._wall_depth, texture=self._wall_texture_params)

            yield wall

            doorstep.start_point = middle_left
            doorstep.end_point = middle_right

        else:

            wall = Wall(start, end, wall_depth=self._wall_depth, texture=self._wall_texture_params)
            yield wall

    # def random_position_on_wall(self, area_coordinates, wall_location, radius_object):
    #
    #     """
    #
    #     Finds a random position on a particular wall.
    #     Used to place a switch.
    #
    #     Args:
    #         area_coordinates: coordinates of the room
    #         wall_location: up, down, left or right
    #         radius_object: size of the scene element to add to the wall.
    #
    #     Returns:
    #
    #     """
    #
    #     area_center, area_size = self.area_rooms[area_coordinates]
    #
    #     pos_x, pos_y = 0, 0
    #
    #     if wall_location == 'up':
    #         pos_y = area_center[1] - area_size[1]/2
    #
    #     elif wall_location == 'down':
    #         pos_y = area_center[1] + area_size[1] / 2
    #
    #     elif wall_location == 'left':
    #         pos_x = area_center[0] - area_size[0] / 2
    #
    #     elif wall_location == 'right':
    #         pos_x = area_center[0] + area_size[0] / 2
    #
    #     else:
    #         raise ValueError
    #
    #     while True:
    #
    #         if wall_location in ['up', 'down']:
    #
    #             pos_x = random.uniform(area_center[0] - area_size[0] / 2,
    #                                    area_center[0] + area_size[0] / 2)
    #
    #         elif wall_location in ['left', 'right']:
    #
    #             pos_y = random.uniform(area_center[1] - area_size[1] / 2,
    #                                    area_center[1] + area_size[1] / 2)
    #
    #         close_to_doorstep = False
    #
    #         for _, doorstep in self.doorsteps.items():
    #             (doorstep_x, doorstep_y), _ = doorstep
    #             if ((doorstep_x - pos_x) ** 2 + (doorstep_y - pos_y)**2)\
    #                     < ((radius_object + self._doorstep_size) / 2) ** 2:
    #                 close_to_doorstep = True
    #
    #         if not close_to_doorstep:
    #             break
    #
    #     return (pos_x, pos_y), 0
    #
    # def get_area(self, room_coordinates, area_location):
    #     """
    #     Get particular area in a room.
    #
    #     Args:
    #         room_coordinates: coordinate of the room.
    #         area_location (str): can be 'up', 'down', 'right', 'left',
    #                              'up-right', 'up-left', 'down-right', or 'down-left'
    #
    #     Returns: center, size
    #
    #     """
    #
    #     area_center, area_size = self.area_rooms[room_coordinates]
    #
    #     if area_location not in ['up', 'down', 'right', 'left',
    #                              'up-right', 'up-left', 'down-right', 'down-left']:
    #         raise ValueError('area_location not correct')
    #
    #     size_y = area_size[1] / 2
    #     if 'up' in area_location:
    #         center_y = area_center[1] - area_size[1] / 4
    #     elif 'down' in area_location:
    #         center_y = area_center[1] + area_size[1] / 4
    #     else:
    #         center_y = area_center[1]
    #         size_y = area_size[1]
    #
    #     size_x = area_size[0] / 2
    #     if 'right' in area_location:
    #         center_x = area_center[0] + area_size[0] / 4
    #     elif 'left' in area_location:
    #         center_x = area_center[0] - area_size[0] / 4
    #     else:
    #         center_x = area_center[0]
    #         size_x = area_size[0]
    #
    #     return [center_x, center_y], [size_x, size_y]



class GridRooms(Playground):
    """
    Multiple rooms with a grid layout.
    Rooms counted top to bottom, left to right, .
    Rooms in row, column numpy style.
    """

    def __init__(self,
                 size: Tuple[int, int],
                 room_layout: Tuple[int, int],
                 doorstep_size: int,
                 random_doorstep_position: bool = True,
                 wall_type='classic',
                 wall_depth=10,
                 playground_seed: Union[int, None] = None,
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

        self._size_door = (wall_depth, doorstep_size)

        self.rng_playground = np.random.default_rng(playground_seed)

        # Wall parameters
        wall_type_params = parse_configuration('playground', wall_type)
        wall_params = {**wall_type_params,
                       **wall_params,
                       'rng': self.rng_playground}
        self._wall_texture_params = wall_params
        self._wall_depth = wall_depth

        # Set random texture for possible replication

        self.grid_rooms = self._generate_rooms(room_layout,
                                               random_doorstep_position,
                                               doorstep_size)

        # By default, an agent starts in a random position of the first room
        first_room = self.grid_rooms[0][0]
        assert isinstance(first_room, RectangleRoom)

        center, size = first_room.center, (first_room.width, first_room.length)
        self.initial_agent_coordinates = CoordinateSampler(center=center,
                                                           area_shape='rectangle',
                                                           width_length=size)

    def _generate_rooms(self,
                        room_layout: Tuple[int, int],
                        random_doorstep_position: bool,
                        doorstep_size: int,
                        ):

        width_room = int(self.size[0] / room_layout[0] - self._wall_depth)
        length_room = int(self.size[1] / room_layout[1] - self._wall_depth)
        size_room = width_room, length_room

        rooms = []

        for c in range(room_layout[0]):

            col_rooms = []

            for r in range(room_layout[1]):

                x_center = (self.size[0] / room_layout[0])*(1/2. + c)
                y_center = (self.size[1] / room_layout[1])*(1/2. + r)

                center = pymunk.Vec2d(x_center, y_center)

                # Doorsteps

                if random_doorstep_position:
                    position = self.rng_playground.integers(doorstep_size, width_room-doorstep_size)
                    doorstep_up = Doorstep(position, doorstep_size, self._wall_depth)

                    position = self.rng_playground.integers(doorstep_size, width_room-doorstep_size)
                    doorstep_down = Doorstep(position, doorstep_size, self._wall_depth)

                    position = self.rng_playground.integers(doorstep_size, length_room-doorstep_size)
                    doorstep_left = Doorstep(position, doorstep_size, self._wall_depth)

                    position = self.rng_playground.integers(doorstep_size, length_room-doorstep_size)
                    doorstep_right = Doorstep(position, doorstep_size, self._wall_depth)

                else:
                    doorstep_up = Doorstep(width_room/2, doorstep_size, self._wall_depth)
                    doorstep_down = Doorstep(width_room/2, doorstep_size, self._wall_depth)
                    doorstep_left = Doorstep(length_room/2, doorstep_size, self._wall_depth)
                    doorstep_right = Doorstep(length_room/2, doorstep_size, self._wall_depth)

                # If doorstep was already decided by other adjacent room

                if c > 0:
                    room_on_left = rooms[c-1][r]
                    assert isinstance(room_on_left, RectangleRoom)
                    position = room_on_left.doorstep_right.position
                    doorstep_left = Doorstep(position, doorstep_size, self._wall_depth)

                if r > 0:
                    room_on_top = col_rooms[-1]
                    assert isinstance(room_on_top, RectangleRoom)
                    position = room_on_top.doorstep_down.position
                    doorstep_up = Doorstep(position, doorstep_size, self._wall_depth)

                if r == room_layout[1] - 1:
                    doorstep_down = None

                if r == 0:
                    doorstep_up = None

                if c == room_layout[0] - 1:
                    doorstep_right = None

                if c == 0:
                    doorstep_left = None

                room = RectangleRoom(center=center,
                                     size=size_room,
                                     doorstep_up=doorstep_up,
                                     doorstep_right=doorstep_right,
                                     doorstep_down=doorstep_down,
                                     doorstep_left=doorstep_left,
                                     wall_depth=self._wall_depth,
                                     wall_texture_params=self._wall_texture_params,
                                     )

                for wall in room.generate_walls():
                    self.add_element(wall)

                col_rooms.append(room)

            rooms.append(col_rooms)

        return rooms



class SingleRoom(GridRooms):

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


class LineRooms(GridRooms):
    """
    Playground composed of connected rooms organized as a line
    """

    def __init__(self, size=(200, 200), room_layout=3, wall_type='classic', **kwargs):

        super().__init__(size=size, room_layout=(room_layout, 1), wall_type=wall_type, **kwargs)
