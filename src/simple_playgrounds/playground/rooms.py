from typing import Union, Dict, Tuple, Optional, List

import numpy as np
import pymunk

from simple_playgrounds.common.position_utils import Coordinate, CoordinateSampler
from simple_playgrounds.common.texture import Texture
from simple_playgrounds.element.elements.basic import Wall, Door
from simple_playgrounds.element.element import SceneElement


class Doorstep:
    def __init__(self, position: float, size: float, depth: float):

        self.position = position
        self.size = size
        self.depth = depth

        self.start_point: Optional[pymunk.Vec2d] = None
        self.end_point: Optional[pymunk.Vec2d] = None

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
        wall_texture: Union[Dict, Texture],
        doorstep_up: Optional[Doorstep] = None,
        doorstep_down: Optional[Doorstep] = None,
        doorstep_left: Optional[Doorstep] = None,
        doorstep_right: Optional[Doorstep] = None,
        rng: Optional[np.random.Generator] = None,
    ):

        assert isinstance(center, (list, tuple)) and len(center) == 2
        assert isinstance(size, (list, tuple)) and len(size) == 2

        self.center = pymunk.Vec2d(*center)
        self.width, self.length = size
        self.size = size

        self._wall_depth = wall_depth
        self._wall_texture = wall_texture

        self.doorstep_up = doorstep_up
        self.doorstep_down = doorstep_down
        self.doorstep_left = doorstep_left
        self.doorstep_right = doorstep_right

        if rng:
            self._rng = rng
        else:
            self._rng = np.random.default_rng()

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
                        texture=self._wall_texture)

            yield wall

            middle_right = start + (end - start).normalized() * (
                doorstep.position + doorstep.size / 2)
            wall = Wall(middle_right,
                        end,
                        wall_depth=self._wall_depth,
                        texture=self._wall_texture)

            yield wall

            doorstep.start_point = middle_left
            doorstep.end_point = middle_right

        else:

            wall = Wall(start,
                        end,
                        wall_depth=self._wall_depth,
                        texture=self._wall_texture)
            yield wall

    def get_area_sampler(self):

        width, length = self.size
        width -= 2 * self._wall_depth
        length -= 2 * self._wall_depth

        return CoordinateSampler(center=self.center,
                                 area_shape='rectangle',
                                 size=(width, length))

    def get_partial_area(
        self,
        area_location: str,
    ) -> Tuple[Tuple[float, float], Tuple[float, float]]:
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
                'down-right', 'down-left', 'left-up', 'right-up', 'left-down',
                'right-down'
        ]:

            raise ValueError('area_location not correct')

        delta_x = self._wall_depth / 2
        delta_y = self._wall_depth / 2

        width, length = self.size
        width -= self._wall_depth
        length -= self._wall_depth

        if 'up' in area_location:
            delta_y = -self.size[1] / 4.
            length /= 2.

        elif 'down' in area_location:
            delta_y = self.size[1] / 4.
            length /= 2.

        if 'right' in area_location:
            delta_x = self.size[0] / 4.
            width /= 2.

        elif 'left' in area_location:
            delta_x = -self.size[0] / 4.
            width /= 2.

        if area_location == 'center':
            length /= 2.
            width /= 2.

        center = self.center + (delta_x, delta_y)

        return (center.x, center.y), (width, length)

    def get_random_position_on_wall(
        self,
        wall_location: str,
        element: SceneElement,
    ) -> Coordinate:
        """

        Finds a random position on a particular wall.
        Used to place a switch.

        Args:
            area_coordinates: coordinates of the room
            wall_location: up, down, left or right
            radius_object: size of the scene element to add to the wall.

        Returns:

        """

        if wall_location == 'up':
            start = pymunk.Vec2d(-self.width / 2 + self._wall_depth / 2,
                                 -self.length / 2 + self._wall_depth / 2)
            end = pymunk.Vec2d(self.width / 2 - self._wall_depth / 2,
                               -self.length / 2 + self._wall_depth / 2)
            doorstep = self.doorstep_up

        elif wall_location == 'down':
            start = pymunk.Vec2d(-self.width / 2 + self._wall_depth / 2,
                                 self.length / 2 - self._wall_depth / 2)
            end = pymunk.Vec2d(self.width / 2 - self._wall_depth / 2,
                               self.length / 2 - self._wall_depth / 2)
            doorstep = self.doorstep_down

        elif wall_location == 'left':
            start = pymunk.Vec2d(-self.width / 2 + self._wall_depth / 2,
                                 -self.length / 2 + self._wall_depth / 2)
            end = pymunk.Vec2d(-self.width / 2 + self._wall_depth / 2,
                               self.length / 2 - self._wall_depth / 2)
            doorstep = self.doorstep_left

        elif wall_location == 'right':
            start = pymunk.Vec2d(self.width / 2 - self._wall_depth / 2,
                                 -self.length / 2 + self._wall_depth / 2)
            end = pymunk.Vec2d(self.width / 2 - self._wall_depth / 2,
                               self.length / 2 - self._wall_depth / 2)
            doorstep = self.doorstep_right

        else:
            raise ValueError

        start = start + (end - start).normalized() * element.radius
        end = end - (end - start).normalized() * element.radius

        if not doorstep:
            return self.center + self._rng.uniform(tuple(start), tuple(end)), (
                start - end).angle

        else:

            middle_1 = start + (end - start).normalized() * (
                doorstep.position - doorstep.size / 2 - element.radius)
            middle_2 = start + (end - start).normalized() * (
                doorstep.position + doorstep.size / 2 + element.radius)

            if middle_1 - start < (0, 0):
                pos = self._rng.uniform(middle_2, end)

            elif end - middle_2 < (0, 0):
                pos = self._rng.uniform(start, middle_1)

            else:
                pos_1 = self._rng.uniform(start, middle_1)
                pos_2 = self._rng.uniform(middle_2, end)

                pos = self._rng.choice([pos_1, pos_2])

        return self.center + pos, (start - end).angle
