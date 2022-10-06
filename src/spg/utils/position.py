"""
Module containing classes to generate random positions and trajectories

"""
from __future__ import annotations

import math
from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Optional, Tuple, Union

import numpy as np

if TYPE_CHECKING:
    from ..playground import Playground

Coordinate = Tuple[Tuple[float, float], float]


class CoordinateSampler(ABC):
    def __init__(
        self,
        playground: Playground,
        center: Tuple[float, float],
        radius: Optional[float] = None,
        width: Optional[float] = None,
        height: Optional[float] = None,
        size: Optional[Tuple[float, float]] = None,
    ):

        self._radius = radius

        if (not width) and size:
            width, height = size

        self._width = width
        self._height = height

        self._center = center

        assert self._radius or self._width

        self._playground = playground

    def _get_relative_positions(self):

        if self._radius:
            pos = np.indices((self._radius, self._radius))
            dist = (pos[0, :] - self._radius / 2) ** 2 + (pos[1, :] - self._radius / 2)
            pos = np.where(dist < (self._radius / 2) ** 2)
            pos = pos - np.atleast_2d((self._radius / 2, self._radius / 2)).transpose()

        elif self._width:

            if self._height:
                pos = np.indices((self._width, self._height)).reshape(2, -1)
                pos = (
                    pos - np.atleast_2d((self._width / 2, self._height / 2)).transpose()
                )

            else:
                pos = np.indices((self._width, self._width)).reshape(2, -1)
                pos = (
                    pos - np.atleast_2d((self._width / 2, self._width / 2)).transpose()
                )

        return pos

    @property
    def _rng(self):
        return self._playground.rng

    @abstractmethod
    def _get_position_pdf(self, position_indices):
        ...

    def _get_random_angle(self):
        return self._rng.uniform(0, 2 * math.pi)

    def sample(self):
        """
        Sample probabiity for all possible coordinates,
        then sort them by order of posterior.
        """

        position_indices = self._get_relative_positions()
        position_pdf = self._get_position_pdf(position_indices)

        uniform_sampling = self._rng.uniform(size=position_pdf.size)
        posterior = uniform_sampling * position_pdf

        rr, cc = position_indices

        stacked = np.stack((rr, cc, posterior), axis=-1).reshape(-1, 3)
        sorted_coordinates = stacked[stacked[:, 2].argsort()]
        sorted_coordinates = sorted_coordinates[::-1]

        for rel_x, rel_y, _ in sorted_coordinates:

            x = self._center[0] + rel_x
            y = self._center[1] + rel_y
            angle = self._get_random_angle()

            yield (x, y), angle


class UniformCoordinateSampler(CoordinateSampler):
    def _get_position_pdf(self, position_indices):
        return np.ones(position_indices.shape[1])


class GaussianCoordinateSampler(CoordinateSampler):
    def __init__(self, playground, sigma, **kwargs):

        self._sigma = sigma
        super().__init__(playground, **kwargs)

    def _get_position_pdf(self, position_indices):
        rr, cc = position_indices
        return np.exp(-(rr**2 + cc**2) / self._sigma**2)


InitCoord = Union[Coordinate, CoordinateSampler]

geometric_shapes = {
    "line": 2,
    "circle": 60,
    "triangle": 3,
    "square": 4,
    "pentagon": 5,
    "hexagon": 6,
}
