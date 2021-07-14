"""
Empty Playgrounds with built-in walls and rooms

"""
from typing import Union, Tuple, Optional, List

import numpy as np

from .playground import Playground
from ..common.position_utils import CoordinateSampler
from ..configs import parse_configuration
from .rooms import Doorstep, RectangleRoom


class GridRooms(Playground):
    """
    Multiple rooms with a grid layout.
    Rooms counted top to bottom, left to right, .
    Rooms in row, column numpy style.
    """
    def __init__(
        self,
        size: Union[List[float], Tuple[float, float]],
        room_layout: Union[List[int], Tuple[int, int]],
        doorstep_size: float,
        random_doorstep_position: bool = True,
        wall_type='classic',
        wall_depth: float = 10,
        playground_seed: Optional[int] = None,
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

        assert isinstance(room_layout, (list, tuple))
        assert len(room_layout) == 2\
               and isinstance(room_layout[0], int)\
               and isinstance(room_layout[1], int)

        super().__init__(size=size)

        self._size_door = (wall_depth, doorstep_size)

        self.rng_playground = np.random.default_rng(playground_seed)

        # Wall parameters
        wall_type_params = parse_configuration('playground', wall_type)
        wall_params = {
            **wall_type_params,
            **wall_params, 'rng': self.rng_playground
        }
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
        self.initial_agent_coordinates = CoordinateSampler(
            center=center, area_shape='rectangle', size=size)

    def _generate_rooms(
        self,
        room_layout,
        random_doorstep_position: bool,
        doorstep_size: float,
    ):

        width_room = self.size[0] / room_layout[0] - self._wall_depth
        length_room = self.size[1] / room_layout[1] - self._wall_depth
        size_room = width_room, length_room

        rooms: List[List[RectangleRoom]] = []

        doorstep_down: Optional[Doorstep]
        doorstep_up: Optional[Doorstep]
        doorstep_left: Optional[Doorstep]
        doorstep_right: Optional[Doorstep]

        for c in range(room_layout[0]):

            col_rooms: List[RectangleRoom] = []

            for r in range(room_layout[1]):

                x_center = (self.size[0] / room_layout[0]) * (1 / 2. + c)
                y_center = (self.size[1] / room_layout[1]) * (1 / 2. + r)

                center = (x_center, y_center)

                # Doorsteps

                if random_doorstep_position:
                    position = self.rng_playground.uniform(
                        doorstep_size, width_room - doorstep_size)
                    doorstep_up = Doorstep(position, doorstep_size,
                                           self._wall_depth)

                    position = self.rng_playground.uniform(
                        doorstep_size, width_room - doorstep_size)
                    doorstep_down = Doorstep(position, doorstep_size,
                                             self._wall_depth)

                    position = self.rng_playground.uniform(
                        doorstep_size, length_room - doorstep_size)
                    doorstep_left = Doorstep(position, doorstep_size,
                                             self._wall_depth)

                    position = self.rng_playground.uniform(
                        doorstep_size, length_room - doorstep_size)
                    doorstep_right = Doorstep(position, doorstep_size,
                                              self._wall_depth)

                else:
                    doorstep_up = Doorstep(width_room / 2, doorstep_size,
                                           self._wall_depth)
                    doorstep_down = Doorstep(width_room / 2, doorstep_size,
                                             self._wall_depth)
                    doorstep_left = Doorstep(length_room / 2, doorstep_size,
                                             self._wall_depth)
                    doorstep_right = Doorstep(length_room / 2, doorstep_size,
                                              self._wall_depth)

                # If doorstep was already decided by other adjacent room

                if c > 0:
                    room_on_left = rooms[c - 1][r]
                    assert isinstance(room_on_left, RectangleRoom)
                    assert isinstance(room_on_left.doorstep_right, Doorstep)
                    position = room_on_left.doorstep_right.position
                    doorstep_left = Doorstep(position, doorstep_size,
                                             self._wall_depth)

                if r > 0:
                    room_on_top = col_rooms[-1]
                    assert isinstance(room_on_top, RectangleRoom)
                    assert isinstance(room_on_top.doorstep_down, Doorstep)
                    position = room_on_top.doorstep_down.position
                    doorstep_up = Doorstep(position, doorstep_size,
                                           self._wall_depth)

                if r == room_layout[1] - 1:
                    doorstep_down = None

                if r == 0:
                    doorstep_up = None

                if c == room_layout[0] - 1:
                    doorstep_right = None

                if c == 0:
                    doorstep_left = None

                room = RectangleRoom(
                    center=center,
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
    def __init__(
        self,
        size,
        wall_type='classic',
        wall_depth=10,
        playground_seed: Union[int, None] = None,
        **wall_params,
    ):

        super().__init__(size=size,
                         room_layout=(1, 1),
                         wall_type=wall_type,
                         doorstep_size=0,
                         wall_depth=wall_depth,
                         playground_seed=playground_seed,
                         **wall_params)

    def _compute_doorsteps(self):
        pass


class LineRooms(GridRooms):
    """
    Playground composed of connected rooms organized as a line
    """
    def __init__(
        self,
        size,
        number_rooms: int,
        doorstep_size,
        random_doorstep_position=True,
        wall_type='classic',
        wall_depth=10,
        playground_seed=None,
        **wall_params,
    ):

        super().__init__(size=size,
                         room_layout=(number_rooms, 1),
                         wall_type=wall_type,
                         doorstep_size=doorstep_size,
                         wall_depth=wall_depth,
                         playground_seed=playground_seed,
                         random_doorstep_position=random_doorstep_position,
                         **wall_params)
