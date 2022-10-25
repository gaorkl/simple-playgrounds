from typing import Tuple

from pymunk import Vec2d

from ..element.wall import ColorWall
from ..playground import Playground
from ..utils.position import UniformCoordinateSampler


class ConnectedRooms(Playground):
    def __init__(
        self,
        size_room: Tuple[int, int],
        room_layout: Tuple[int, int],
        doorstep_length: float,
        centered_doorstep: bool = True,
        seed=None,
        background=None,
        wall_cls=ColorWall,
        wall_color=None,
        **kwargs,
    ):

        size = (size_room[0] * room_layout[0], size_room[1] * room_layout[1])

        self._size_room = size_room
        self._room_layout = room_layout

        self._doorstep_length = doorstep_length
        self._centered_doorstep = centered_doorstep
        self._color = wall_color

        super().__init__(size, seed, background, **kwargs)

        self._room_coordinates = self._get_room_coordinates()
        self._room_centers, self._room_corners = self._get_room_positions()

        self._wall_cls = wall_cls
        self._doorsteps = self._add_walls()

        self._room_coordinate_sampler = self._get_coord_sampler()

    def _get_room_coordinates(self):

        room_coordinates = []

        for x in range(self._room_layout[0]):
            for y in range(self._room_layout[1]):
                room_coordinates.append((x, y))

        return room_coordinates

    def _get_room_positions(self):

        room_centers = []
        room_corners = []

        corner_x, corner_y = -self.size[0] / 2, -self.size[1] / 2

        for (ind_x, ind_y) in self._room_coordinates:
            l_x = corner_x + ind_x * self._size_room[0]
            r_x = corner_x + (ind_x + 1) * self._size_room[0]
            b_y = corner_y + ind_y * self._size_room[1]
            t_y = corner_y + (ind_y + 1) * self._size_room[1]

            c_x = corner_x + (ind_x + 0.5) * self._size_room[0]
            c_y = corner_y + (ind_y + 0.5) * self._size_room[1]

            room_centers.append((c_x, c_y))
            room_corners.append(((l_x, b_y), (l_x, t_y), (r_x, t_y), (r_x, b_y)))

        return room_centers, room_corners

    def _add_walls(self):

        doorsteps = {}

        for (ind_x, ind_y), corners in zip(self._room_coordinates, self._room_corners):

            corn_bl, corn_tl, corn_tr, corn_br = corners

            if ind_x == 0:
                self._add_wall(corn_bl, corn_tl)

            if ind_x == self._room_layout[0] - 1:
                self._add_wall(corn_br, corn_tr)
            else:
                doorstep_pos = self._add_wall(corn_br, corn_tr, doorstep=True)
                if doorstep_pos:
                    doorsteps[(ind_x, ind_y), (ind_x + 1, ind_y)] = doorstep_pos

            if ind_y == 0:
                self._add_wall(corn_bl, corn_br)

            if ind_y == self._room_layout[1] - 1:
                self._add_wall(corn_tl, corn_tr)
            else:
                doorstep_pos = self._add_wall(corn_tl, corn_tr, doorstep=True)
                if doorstep_pos:
                    doorsteps[(ind_x, ind_y), (ind_x, ind_y + 1)] = doorstep_pos

        return doorsteps

    def _add_wall(self, pos_1, pos_2, doorstep=False):

        if not self._color:
            color = list(self._rng.integers(0, 255, 3))
        else:
            color = self._color

        if not doorstep:
            wall = self._wall_cls(pos_1, pos_2, width=10, color=color)
            self.add(wall, wall.wall_coordinates)
            return False

        pt_1 = Vec2d(*pos_1)
        pt_2 = Vec2d(*pos_2)
        angle = (pt_2 - pt_1).angle
        unit_vec = (pt_2 - pt_1).normalized()
        length = (pt_2 - pt_1).length

        if self._centered_doorstep:
            pt_doorstep = (pt_2 + pt_1) / 2
            pos = length / 2

        else:
            pos = self._rng.uniform(
                self._doorstep_length / 2, length - self._doorstep_length / 2
            )

        pt_doorstep = pt_1 + unit_vec * pos

        pt_ds_1 = pt_1 + unit_vec * (pos - self._doorstep_length / 2)
        pt_ds_2 = pt_1 + unit_vec * (pos + self._doorstep_length / 2)

        wall = self._wall_cls(pos_1, pt_ds_1, width=10, color=color)
        self.add(wall, wall.wall_coordinates)

        wall = self._wall_cls(pt_ds_2, pos_2, width=10, color=color)
        self.add(wall, wall.wall_coordinates)

        return (pt_doorstep.x, pt_doorstep.y), angle

    def _get_coord_sampler(self):

        samplers = []

        for center in self._room_centers:

            sampler = UniformCoordinateSampler(
                self, center, width=self._size_room[0], height=self._size_room[1]
            )
            samplers.append(sampler)

        return samplers


class Room(ConnectedRooms):
    def __init__(
        self,
        size: Tuple[int, int],
        seed=None,
        background=None,
        wall_cls=ColorWall,
        wall_color=None,
        **kwargs,
    ):

        super().__init__(
            size_room=size,
            room_layout=(1, 1),
            doorstep_length=10,
            centered_doorstep=True,
            seed=seed,
            background=background,
            wall_cls=wall_cls,
            wall_color=wall_color,
            **kwargs,
        )
