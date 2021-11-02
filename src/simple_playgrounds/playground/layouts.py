"""
Empty Playgrounds with built-in walls and rooms

"""
from typing import Union, Tuple, Optional, List, Dict

import numpy as np

from simple_playgrounds.playground.playground import Playground
from simple_playgrounds.playground.rooms import Doorstep, RectangleRoom
from simple_playgrounds.common.position_utils import CoordinateSampler
from simple_playgrounds.configs import parse_configuration
from simple_playgrounds.common.texture import TextureGenerator, ColorTexture, Texture
from simple_playgrounds.common.definitions import WALL_DEPTH

class GridRooms(Playground):
    """
    Multiple rooms with a grid layout.
    Rooms counted top to bottom, left to right, .
    Rooms in row, column numpy style.
    """
    def __init__(
        self,
        size: Tuple[int, int],
        room_layout: Union[List[int], Tuple[int, int]],
        doorstep_size: float,
        random_doorstep_position: bool = True,
        wall_type: Optional[str] = 'classic',
        wall_depth: Optional[float] = WALL_DEPTH,
        playground_seed: Optional[int] = None,
        wall_texture: Optional[Union[Texture, Dict, Tuple[int, int, int]]] = None,
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


        Wall texture takes priority on wall type.
        Several wall types are already implemented: classic, light, dark, colorful

        """

        # Playground Layout

        assert isinstance(room_layout, (list, tuple))
        assert len(room_layout) == 2\
               and isinstance(room_layout[0], int)\
               and isinstance(room_layout[1], int)

        self.width_room = size[0] / room_layout[1]
        self.length_room = size[1] / room_layout[0]

        # Check that there is enough space for doorsteps
        if self.width_room - 2*wall_depth < doorstep_size \
                or self.length_room - 2*wall_depth < doorstep_size:
            raise ValueError("Doorstep too large wrt room size")

        super().__init__(size=size)

        self._size_door = (wall_depth, doorstep_size)

        self.rng_playground = np.random.default_rng(playground_seed)

        # If wall texture is provided, use it

        if isinstance(wall_texture, Dict):
            wall_texture = TextureGenerator.create(**wall_texture, rng=self.rng_playground)

        elif isinstance(wall_texture, (tuple, list)):
            wall_texture = ColorTexture(color=wall_texture)

        # if not, use default
        if not wall_texture:

            # Wall parameters
            default_wall_texture_params = parse_configuration('playground', wall_type)
            wall_texture = TextureGenerator.create(**default_wall_texture_params, rng=self.rng_playground)

        assert isinstance(wall_texture, Texture)

        self._wall_texture = wall_texture
        self._wall_depth = wall_depth

        # Set random texture for possible replication

        self.grid_rooms = self._generate_rooms(room_layout,
                                               random_doorstep_position,
                                               doorstep_size)

        # By default, an agent starts in a random position of the first room
        first_room = self.grid_rooms[0, 0]
        assert isinstance(first_room, RectangleRoom)

        center_first_room = first_room.center
        size_first_room = first_room.width - 2 * wall_depth, first_room.length - 2 * wall_depth

        self.initial_agent_coordinates = CoordinateSampler(
            center=center_first_room,
            area_shape='rectangle',
            size=size_first_room)

    def _generate_rooms(
        self,
        room_layout: Union[List[int], Tuple[int, int]],
        random_doorstep_position: bool,
        doorstep_size: float,
    ):

        size_room = self.width_room, self.length_room

        rooms = np.empty(room_layout, RectangleRoom)

        doorstep_down: Optional[Doorstep]
        doorstep_up: Optional[Doorstep]
        doorstep_left: Optional[Doorstep]
        doorstep_right: Optional[Doorstep]

        for r in range(room_layout[0]):

            for c in range(room_layout[1]):

                # Difference pymunk coord and numpy indexing
                x_center = self.width_room * (1 / 2. + c)
                y_center = self.length_room * (1 / 2. + r)

                center = (x_center, y_center)

                # Doorsteps

                if random_doorstep_position:
                    position = self.rng_playground.uniform(
                        doorstep_size / 2, self.width_room - doorstep_size / 2)
                    doorstep_up = Doorstep(position, doorstep_size,
                                           self._wall_depth)

                    position = self.rng_playground.uniform(
                        doorstep_size / 2, self.width_room - doorstep_size / 2)
                    doorstep_down = Doorstep(position, doorstep_size,
                                             self._wall_depth)

                    position = self.rng_playground.uniform(
                        doorstep_size / 2,
                        self.length_room - doorstep_size / 2)
                    doorstep_left = Doorstep(position, doorstep_size,
                                             self._wall_depth)

                    position = self.rng_playground.uniform(
                        doorstep_size / 2,
                        self.length_room - doorstep_size / 2)
                    doorstep_right = Doorstep(position, doorstep_size,
                                              self._wall_depth)

                else:
                    doorstep_up = Doorstep(self.width_room / 2, doorstep_size,
                                           self._wall_depth)
                    doorstep_down = Doorstep(self.width_room / 2,
                                             doorstep_size, self._wall_depth)
                    doorstep_left = Doorstep(self.length_room / 2,
                                             doorstep_size, self._wall_depth)
                    doorstep_right = Doorstep(self.length_room / 2,
                                              doorstep_size, self._wall_depth)

                # If doorstep was already decided by other adjacent room

                if c > 0:
                    room_on_left = rooms[r, c - 1]
                    assert isinstance(room_on_left, RectangleRoom)
                    assert isinstance(room_on_left.doorstep_right, Doorstep)
                    position = room_on_left.doorstep_right.position
                    doorstep_left = Doorstep(position, doorstep_size,
                                             self._wall_depth)

                if r > 0:
                    room_on_top = rooms[r - 1, c]
                    assert isinstance(room_on_top, RectangleRoom)
                    assert isinstance(room_on_top.doorstep_down, Doorstep)
                    position = room_on_top.doorstep_down.position
                    doorstep_up = Doorstep(position, doorstep_size,
                                           self._wall_depth)

                if r == room_layout[0] - 1:
                    doorstep_down = None

                if r == 0:
                    doorstep_up = None

                if c == room_layout[1] - 1:
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
                    wall_texture=self._wall_texture,
                )

                for wall in room.generate_walls():
                    self.add_element(wall)

                rooms[r, c] = room

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
        playground_seed: Optional[int] = None,
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
                         room_layout=(1, number_rooms),
                         wall_type=wall_type,
                         doorstep_size=doorstep_size,
                         wall_depth=wall_depth,
                         playground_seed=playground_seed,
                         random_doorstep_position=random_doorstep_position,
                         **wall_params)
