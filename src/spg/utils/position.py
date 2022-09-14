"""
Module containing classes to generate random positions and trajectories

"""
from __future__ import annotations

import math
from abc import ABC, abstractmethod
from collections.abc import Generator
from typing import TYPE_CHECKING, Optional, Tuple, Union

import numpy as np

from .contour import Contour

if TYPE_CHECKING:
    from ..entity import EmbodiedEntity

Coordinate = Tuple[Tuple[float, float], float]


class CoordinateSampler(ABC):
    """Sampler for a random position within a particular area

    Example:
        area_1 = PositionAreaSampler(area_shape='rectangle',
                                    center=[70, 70], shape=[30, 100])
        area_2 = PositionAreaSampler(area_shape='gaussian',
                                    center=[150, 50], variance = 300, radius=60)

    """

    def __init__(
        self,
        distribution: str,
        contour: Contour,
        angle: Optional[Union[float, Tuple[float, float]]] = None,
        **kwargs,
    ):

        if contour:
            self._contour = contour
        else:
            self._contour = Contour(**kwargs)

        self._rng = np.random.default_rng()

        self._contour = contour
        self._pdf = self._get_pdf(distribution, **kwargs)

        self._angle_range = (-math.pi, math.pi)
        if angle:
            if isinstance(angle, float):
                self._angle_range = (angle, angle)
            elif isinstance(angle, tuple):
                assert len(angle) == 2
                self._angle_range = angle

    def _get_pdf(
        self,
        distribution: str,
        sigma: Optional[float] = None,
    ):

        width, length = self._contour.mask_size
        center_r, center_c = self._contour.mask_center

        rr, cc = np.indices((width, length))
        pdf = np.zeros((width, length))

        if distribution == "gaussian":
            assert sigma
            pdf[rr, cc] = np.exp(
                -((rr - center_r) ** 2 + (cc - center_c) ** 2) / sigma**2
            ) / math.sqrt(2 * math.pi * sigma)

        elif distribution == "uniform":
            pdf[rr, cc] = 1 / (width * length)

        return pdf

    @property
    def rng(self):
        return self._rng

    @rng.setter
    def rng(self, rng):
        self._rng = rng

    @property
    @abstractmethod
    def _center(self) -> Tuple[float, float]:
        ...

    def sample(self):
        """
        Sample probabiity for all possible coordinates,
        then sort them by order of posterior.
        """

        uniform_sampling = self._rng.uniform(size=self._contour.mask_size)
        posterior = uniform_sampling * self._pdf
        rr, cc = np.indices(self._contour.mask_size)
        mask = self._contour.mask

        stacked = np.stack((rr, cc, mask, posterior), axis=-1).reshape(-1, 4)
        sorted_coordinates = stacked[stacked[:, 2].argsort()]

        for coord in sorted_coordinates:
            in_contour = coord[2]
            if in_contour:
                x = coord[0] - self._contour.mask_center[0] + self._center[0]
                y = self._contour.mask_center[1] - coord[1] + self._center[1]

                yield (x, y), self._rng.uniform(*self._angle_range)


class FixedCoordinateSampler(CoordinateSampler):
    def __init__(self, position: Tuple[float, float], **kwargs):

        super().__init__(**kwargs)
        self._center_position = position

    @property
    def _center(self):
        return self._center_position


class AnchoredCoordinateSampler(CoordinateSampler):
    def __init__(self, anchor: EmbodiedEntity, **kwargs):
        self._anchor = anchor
        super().__init__(**kwargs)

    @property
    def _center(self):
        return self._anchor.position


class Trajectory(Generator):
    """Trajectory is a generator used to define a list of positions that an entity follows.

    Example:
    trajectory = Trajectory('waypoints',
               300, waypoints=[[20, 20], [20, 180], [180,180], [180,20]])
    trajectory = Trajectory('shape',
               200, 8, shape='square', center=[100, 70, 0], radius=50)

    """

    def __init__(
        self,
        trajectory_type: str,
        trajectory_duration: int,
        n_rotations: int = 0,
        index_start: int = 0,
        **kwargs,
    ):
        """Trajectory follows waypoints or shape.

        Args:
            trajectory_type (str): 'waypoints' or 'shape'
            trajectory_duration (:obj:'int'): number of steps
                to complete a full trajectory
            n_rotations (:obj:'int'): number of entity rotations
                during one full trajectory.
                Default is 0.
            index_start (:obj:'int'): offset for the start of the
                trajectory.
                Default is 0.
            **kwargs: Arbitrary keyword arguments

        Keyword Arguments:
            shape (str): 'line', 'circle', 'square', 'pentagpn', 'hexagon'
            center (:obj:'list' of :obj:'int'): coordinates of the center of a shape
            radius (:obj:'int'): radius of the shape that entity is following
            waypoints (:obj:'list' of :obj:'int'): list of waypoints
            counter_clockwise (:obj:'bool): direction of trajectory. Default is False

        """

        self.trajectory_duration = trajectory_duration
        self.trajectory_type = trajectory_type
        self.n_rotations = n_rotations

        # Calculate waypoints when trajectory_type is shape
        if self.trajectory_type == "shape":
            self.shape = kwargs["shape"]
            self.radius = kwargs["radius"]
            self.center = kwargs["center"]
            self.orientation_shape = self.center[2]
            self.waypoints = self._generate_geometric_waypoints()

        elif self.trajectory_type == "waypoints":
            self.waypoints = kwargs["waypoints"]

        # Generate all trajectory points based on waypoints
        self.trajectory_points = self._generate_trajectory()

        self._index_start = index_start
        self.current_index = self._index_start

        self.counter_clockwise = kwargs.get("counter_clockwise", False)

    @property
    def _index_start(self):

        if self.trajectory_type == "shape":
            number_sides = geometric_shapes[self.shape]

            # Center the starting point on the x axis, angle 0
            return self._idx_start - int(len(self.trajectory_points) / number_sides / 2)

        return self._idx_start

    @_index_start.setter
    def _index_start(self, index_start):

        self._idx_start = index_start

    def _generate_geometric_waypoints(self):

        number_sides = geometric_shapes[self.shape]
        offset_angle = math.pi / number_sides + self.orientation_shape

        waypoints = []
        for num_side in range(number_sides):
            waypoints.append(
                [
                    self.center[0]
                    + self.radius
                    * math.cos(num_side * 2 * math.pi / number_sides + offset_angle),
                    self.center[1]
                    + self.radius
                    * math.sin(num_side * 2 * math.pi / number_sides + offset_angle),
                    0,
                ]
            )

        return waypoints[::-1]

    def _generate_trajectory(self):

        shifted_waypoints = self.waypoints[1:] + self.waypoints[:1]
        total_length = sum(
            math.sqrt((x1[0] - x2[0]) ** 2 + (x1[1] - x2[1]) ** 2)
            for x1, x2 in zip(self.waypoints, shifted_waypoints)
        )

        trajectory_points = []

        for pt_1, pt_2 in zip(self.waypoints, shifted_waypoints):

            distance_between_points = math.sqrt(
                (pt_1[0] - pt_2[0]) ** 2 + (pt_1[1] - pt_2[1]) ** 2
            )

            # Ratio of trajectory points between these two waypoints
            ratio_points = distance_between_points / total_length
            n_points = int(self.trajectory_duration * ratio_points)

            pts_x = [
                pt_1[0] + x * (pt_2[0] - pt_1[0]) / n_points for x in range(n_points)
            ]
            pts_y = [
                pt_1[1] + x * (pt_2[1] - pt_1[1]) / n_points for x in range(n_points)
            ]

            for i in range(n_points):
                trajectory_points.append([(pts_x[i], pts_y[i]), 0])

        for pt_index, trajectory_point in enumerate(trajectory_points):

            angle = (
                (pt_index * self.n_rotations)
                * (2 * math.pi)
                / len(trajectory_points)
                % (2 * math.pi)
            )

            trajectory_point[1] = angle

        return trajectory_points

    def send(self, ignored_args) -> Coordinate:
        """Function for generator.
        Sends current position, then changes current position
        depending on rotation side.

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
    def throw(self, typ=None, val=None, tb=None):
        raise StopIteration

    def reset(self, index_start=None):
        """Resets the trajectory to its initial position.

        Args:
            index_start (:obj:'list' of :obj:'int'): optional.
            If provided, changes the initial index for trajectory

        Returns:

        """
        if index_start is not None:
            self._index_start = index_start

        self.current_index = self._index_start


InitCoord = Union[Coordinate, CoordinateSampler]

geometric_shapes = {
    "line": 2,
    "circle": 60,
    "triangle": 3,
    "square": 4,
    "pentagon": 5,
    "hexagon": 6,
}
