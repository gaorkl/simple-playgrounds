"""
Module containing classes to generate random positions and trajectories

"""
from typing import Tuple, Optional, Union

import pymunk
import random
import math
from collections.abc import Generator

import numpy as np

Coordinate = Tuple[Tuple[float, float], float]


class CoordinateSampler:
    """ Sampler for a random position within a particular area

    Example:
        area_1 = PositionAreaSampler(area_shape='rectangle', center=[70, 70], shape=[30, 100])
        area_2 = PositionAreaSampler(area_shape='gaussian', center=[150, 50], variance = 300, radius=60)

    """
    def __init__(
        self,
        center: Tuple[float, float],
        area_shape: str,
        size: Optional[Tuple[float, float]] = None,
        radius: Optional[float] = None,
        std: Optional[float] = None,
        angle_range: Optional[Tuple[float, float]] = None,
        min_size: Tuple[float, float] = (0, 0),
        min_radius: float = 0,
        angle: float = 0,
    ):
        """

        Args:
            center (:obj: list of :obj: int): x, y coordinates of the center of the area
            area_shape (str): 'circle', 'gaussian' or 'rectangle'
            **kwargs: Keyword arguments depending on the area_shape

        Keyword Arguments:
            width_length (:obj: list of :obj: int): Width and Length of the rectangle shape
            radius (int): radius of the gaussian and circle shape
            std (int): variance of the gaussian

        """

        self._area_shape = area_shape

        assert len(center) == 2
        self._center = center
        self._angle = angle

        if angle_range:
            assert len(angle_range) == 2
            self._angle_range = angle_range
        else:
            self._angle_range = (-math.pi, math.pi)

        # Area shape
        if self._area_shape == 'rectangle':

            assert size and len(size) == 2

            self._width, self._length = size
            self._min_width, self._min_length = min_size

            assert self._width > self._min_width
            assert self._length > self._min_length

        elif self._area_shape == 'circle':

            assert radius

            self._radius = radius
            self._min_radius = min_radius

            assert self._radius > self._min_radius

        elif self._area_shape == 'gaussian':

            assert radius
            assert std

            self._radius = radius
            self._min_radius = min_radius
            assert self._radius > self._min_radius

            self._std = std

        else:
            raise ValueError('area shape not implemented')

    def sample(self,
               coordinates: Optional[Coordinate] = None) -> Coordinate:

        x, y, theta = 0., 0., 0.

        if not coordinates:
            center = self._center
            theta = random.uniform(*self._angle_range)

        else:
            center, theta = coordinates

        if self._area_shape == 'rectangle':
            # split the rectangle to horizontal and vertical pieces,
            # choose based on h_threshold and then sample uniformly and shift

            found_position = False

            while not found_position:
                x = random.uniform(-self._width / 2, self._width / 2)
                y = random.uniform(-self._length / 2, self._length / 2)

                if not (-self._min_width / 2 < x < self._min_width / 2
                        and -self._min_length / 2 < y < self._min_length / 2):
                    found_position = True

        elif self._area_shape == 'circle':

            found_position = False

            while not found_position:
                x = random.uniform(-self._radius, self._radius)
                y = random.uniform(-self._radius, self._radius)

                r = math.sqrt(x**2 + y**2)
                if self._min_radius < r < self._radius:
                    found_position = True

        elif self._area_shape == 'gaussian':

            found_position = False

            while not found_position:
                x, y = np.random.multivariate_normal(
                    (0, 0),
                    ((self._std**2, 0), (0, self._std**2)),
                )
                r = math.sqrt(x**2 + y**2)
                if self._min_radius < r < self._radius:
                    found_position = True

        else:

            raise ValueError('Not implemented')

        rel_pos = pymunk.Vec2d(x, y).rotated(self._angle)
        pos = tuple(rel_pos + center)

        return pos, theta


class Trajectory(Generator):
    """ Trajectory is a generator which is used to define a list of positions that an entity follows.

    Example:
    trajectory = Trajectory('waypoints', 300, waypoints=[[20, 20], [20, 180], [180,180], [180,20]])
    trajectory = Trajectory('shape', 200, 8, shape='square', center=[100, 70, 0], radius=50)

    """
    def __init__(self,
                 trajectory_type,
                 trajectory_duration,
                 n_rotations=0,
                 index_start=0,
                 **kwargs):
        """ Trajectory follows waypoints or shape.

        Args:
            trajectory_type (str): 'waypoints' or 'shape'
            trajectory_duration (:obj:'int'): number of steps to complete a full trajectory
            n_rotations (:obj:'int'): number of entity rotations during one full trajectory.
                Default is 0.
            index_start (:obj:'int'): offset for the start of the trajectory
                Default is 0.
            **kwargs: Arbitrary keyword arguments

        Keyword Arguments:
            shape (str): 'line', 'circle', 'square', 'pentagpn', 'hexagon'
            center (:obj:'list' of :obj:'int'): if shape is used, (x,y,orientation) of the center of a shape
            radius (:obj:'int'): if shape is used, radius of the shape that entity is following
            waypoints (:obj:'list' of :obj:'int'): if 'waypoints' is used, list of waypoints
            counter_clockwise (:obj:'bool): direction of the trajectory. Default is False

        """

        self.trajectory_duration = trajectory_duration
        self.trajectory_type = trajectory_type
        self.n_rotations = n_rotations

        # Calculate waypoints when trajectory_type is shape
        if self.trajectory_type == 'shape':
            self.shape = kwargs['shape']
            self.radius = kwargs['radius']
            self.center = kwargs['center']
            self.orientation_shape = self.center[2]
            self.waypoints = self._generate_geometric_waypoints()

        elif self.trajectory_type == 'waypoints':
            self.waypoints = kwargs['waypoints']

        # Generate all trajectory points based on waypoints
        self.trajectory_points = self._generate_trajectory()

        self._index_start = index_start
        self.current_index = self._index_start

        self.counter_clockwise = kwargs.get('counter_clockwise', False)

    @property
    def _index_start(self):

        if self.trajectory_type == 'shape':
            number_sides = geometric_shapes[self.shape]

            # Center the starting point on the x axis, angle 0
            return self._idx_start - int(
                len(self.trajectory_points) / number_sides / 2)

        return self._idx_start

    @_index_start.setter
    def _index_start(self, index_start):

        self._idx_start = index_start

    def _generate_geometric_waypoints(self):

        number_sides = geometric_shapes[self.shape]
        offset_angle = math.pi / number_sides + self.orientation_shape

        waypoints = []
        for num_side in range(number_sides):
            waypoints.append([
                self.center[0] + self.radius *
                math.cos(num_side * 2 * math.pi / number_sides + offset_angle),
                self.center[1] + self.radius *
                math.sin(num_side * 2 * math.pi / number_sides + offset_angle),
                0
            ])

        return waypoints[::-1]

    def _generate_trajectory(self):

        shifted_waypoints = self.waypoints[1:] + self.waypoints[:1]
        total_length = sum([
            math.sqrt((x1[0] - x2[0])**2 + (x1[1] - x2[1])**2)
            for x1, x2 in zip(self.waypoints, shifted_waypoints)
        ])

        trajectory_points = []

        for pt_1, pt_2 in zip(self.waypoints, shifted_waypoints):

            distance_between_points = math.sqrt((pt_1[0] - pt_2[0])**2 +
                                                (pt_1[1] - pt_2[1])**2)

            # Ratio of trajectory points between these two waypoints
            ratio_points = distance_between_points / total_length
            n_points = int(self.trajectory_duration * ratio_points)

            pts_x = [
                pt_1[0] + x * (pt_2[0] - pt_1[0]) / n_points
                for x in range(n_points)
            ]
            pts_y = [
                pt_1[1] + x * (pt_2[1] - pt_1[1]) / n_points
                for x in range(n_points)
            ]

            for i in range(n_points):
                trajectory_points.append([(pts_x[i], pts_y[i]), 0])

        for pt_index, trajectory_point in enumerate(trajectory_points):

            angle = (pt_index * self.n_rotations) * (
                2 * math.pi) / len(trajectory_points) % (2 * math.pi)

            trajectory_point[1] = angle

        return trajectory_points

    def send(self, ignored_args):
        """ Function for generator. Sends current position, then changes current position depending on rotation side.

        Args:
            ignored_args:

        Returns:
            position ('obj' list of :obj:'int'): next (x,y,theta) position

        """
        returned_value = self.trajectory_points[self.current_index]

        if self.counter_clockwise:
            self.current_index -= 1
            if self.current_index == -(len(self.trajectory_points)):
                self.current_index = 0

        else:
            self.current_index += 1
            if self.current_index == len(self.trajectory_points):
                self.current_index = 0

        return returned_value

    # pylint: disable=redefined-builtin
    # pylint: disable=arguments-differ
    def throw(self, type=None, value=None, traceback=None):
        raise StopIteration

    def reset(self, index_start=None):
        """Resets the trajectory to its initial position.

        Args:
            index_start (:obj:'list' of :obj:'int'): optional. If provided, changes the initial index for trajectory

        Returns:

        """
        if index_start is not None:
            self._index_start = index_start

        self.current_index = self._index_start


InitCoord = Union[Coordinate, CoordinateSampler,
                  Trajectory, ]


#
# def get_relative_position_of_entities(entity_1, entity_2):
#     """
#     Calculates the relative position of entity_2 wrt entity_1.
#
#     Args:
#         entity_1 (:obj: Entity): reference Entity.
#         entity_2 (:obj: Entity):
#
#     Returns:
#
#     """
#
#     entity_1_x, entity_1_y, entity_1_angle = entity_1.position
#     entity_2_x, entity_2_y, entity_2_angle = entity_2.position
#
#     relative_angle = (entity_2_angle - entity_1_angle)%(2*math.pi)
#
#     relative_x = (entity_2_x - entity_1_x)*math.cos(-entity_1_angle) \
#                  - (entity_2_y - entity_1_y)*math.sin(-entity_1_angle)
#     relative_y = (entity_2_x - entity_1_x)*math.sin(-entity_1_angle) \
#                  + (entity_2_y - entity_1_y)*math.cos(-entity_1_angle)
#
#     return relative_x, relative_y, relative_angle
geometric_shapes = {
    'line': 2,
    'circle': 60,
    'triangle': 3,
    'square': 4,
    'pentagon': 5,
    'hexagon': 6
}