from typing import Union, Dict, Tuple, Optional, List

import pymunk

from simple_playgrounds.common.texture import Texture
from simple_playgrounds.elements.collection.basic import Wall, Door


class Doorstep:
    def __init__(self, position, size, depth):

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

        door = Door(start_point=self.start_point,
                    end_point=self.end_point,
                    door_depth=self.depth,
                    **door_params)

        return door


class RectangleRoom:
    def __init__(
        self,
        center: Union[List[float], Tuple[float, float]],
        size: Union[List[float], Tuple[float, float]],
        wall_depth: float,
        wall_texture_params: Union[Dict, Texture],
        doorstep_up: Optional[Doorstep] = None,
        doorstep_down: Optional[Doorstep] = None,
        doorstep_left: Optional[Doorstep] = None,
        doorstep_right: Optional[Doorstep] = None,
    ):

        assert isinstance(center, (list, tuple)) and len(center) == 2
        assert isinstance(size, (list, tuple)) and len(size) == 2

        self.center = pymunk.Vec2d(*center)
        self.width, self.length = size
        self.size = size

        self._wall_depth = wall_depth
        self._wall_texture_params = wall_texture_params

        self.doorstep_up = doorstep_up
        self.doorstep_down = doorstep_down
        self.doorstep_left = doorstep_left
        self.doorstep_right = doorstep_right

        # self._doors = {}

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

    def _generate_wall(self, start: pymunk.Vec2d, end: pymunk.Vec2d,
                       doorstep: Doorstep):

        if doorstep:
            assert isinstance(doorstep, Doorstep)

            middle_left = start + (end - start).normalized() * (
                doorstep.position - doorstep.size / 2)
            wall = Wall(start,
                        middle_left,
                        wall_depth=self._wall_depth,
                        texture=self._wall_texture_params)

            yield wall

            middle_right = start + (end - start).normalized() * (
                doorstep.position + doorstep.size / 2)
            wall = Wall(middle_right,
                        end,
                        wall_depth=self._wall_depth,
                        texture=self._wall_texture_params)

            yield wall

            doorstep.start_point = middle_left
            doorstep.end_point = middle_right

        else:

            wall = Wall(start,
                        end,
                        wall_depth=self._wall_depth,
                        texture=self._wall_texture_params)
            yield wall

    def get_partial_area(
        self,
        area_location: str,
    ):
        """
        Get particular area in a room.

        Args:
            room_coordinates: coordinate of the room.
            area_location (str): can be 'up', 'down', 'right', 'left',
                                 'up-right', 'up-left', 'down-right', or 'down-left'

        Returns: center, size

        """

        if area_location not in [
                'center', 'up', 'down', 'right', 'left', 'up-right', 'up-left',
                'down-right', 'down-left'
        ]:

            raise ValueError('area_location not correct')

        delta_x = 0
        delta_y = 0
        width, length = self.size

        if 'up' in area_location:
            delta_y = -self.size[1] / 4
            length /= 2.

        elif 'down' in area_location:
            delta_y = self.size[1] / 4
            length /= 2.

        if 'right' in area_location:
            delta_x = self.size[0] / 4
            width /= 2.

        elif 'left' in area_location:
            delta_x = -self.size[0] / 4
            width /= 2.

        if area_location == 'center':
            length /= 2.
            width /= 2.

        return self.center + (delta_x, delta_y), (width, length)

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
