import math
from enum import IntEnum, auto
from typing import List, Optional, Tuple, Union

import numpy as np
import pymunk
import skimage.draw


class GeometricShapes(IntEnum):
    LINE = 2
    TRIANGLE = 3
    SQUARE = 4
    PENTAGON = 5
    HEXAGON = 6
    CIRCLE = 60
    RECTANGLE = auto()
    POLYGON = auto()


class Contour:
    def __init__(
        self,
        shape: Union[str, GeometricShapes],
        **kwargs,
    ):

        self._shape: GeometricShapes
        self._radius: Optional[float] = None
        self._size: Optional[Tuple[float, float]] = None
        self._vertices: Optional[List[Tuple[float, float]]] = None

        if isinstance(shape, str):
            shape = GeometricShapes[shape.upper()]
        self._shape = shape
        self._get_contour_from_shape(**kwargs)

        self._mask = self.compute_mask()

    @property
    def size(self):
        return self._size

    @property
    def radius(self):
        return self._radius

    @property
    def shape(self):
        return self._shape

    @property
    def vertices(self):
        return self._vertices

    @property
    def dict_attributes(self):
        return {
            "shape": self._shape,
            "radius": self._radius,
            "vertices": self._vertices,
            "size": self._size,
        }

    @property
    def mask(self):
        return self._mask

    @property
    def mask_size(self):
        return self._mask_size

    @property
    def mask_center(self):
        return self._mask_center

    def _get_contour_from_shape(
        self,
        radius: Optional[float] = None,
        size: Optional[Tuple[float, float]] = None,
        vertices: Optional[List[Tuple[float, float]]] = None,
        **_,
    ):

        # Dimensions of the entity

        if self._shape in [
            GeometricShapes.TRIANGLE,
            GeometricShapes.SQUARE,
            GeometricShapes.PENTAGON,
            GeometricShapes.HEXAGON,
            GeometricShapes.CIRCLE,
        ]:
            assert radius is not None and isinstance(radius, (float, int))

            self._radius = radius
            self._size = (2 * radius, 2 * radius)
            self._vertices = self._get_vertices()

        elif self._shape == GeometricShapes.RECTANGLE:
            assert size is not None and len(size) == 2

            width, length = size
            self._radius = ((width / 2) ** 2 + (length / 2) ** 2) ** (1 / 2)
            self._size = size
            self._vertices = self._get_vertices()

        elif self._shape == GeometricShapes.POLYGON:
            assert vertices and len(vertices) > 1

            vertices = np.array(vertices)
            center = np.mean(vertices, axis=0)
            vertices = vertices - center

            radius = np.max(np.linalg.norm(vertices, axis=1))
            self._size = (2 * radius, 2 * radius)
            self._radius = radius
            self._vertices = [pymunk.Vec2d(*pt) for pt in vertices]

        else:
            raise ValueError(f"Wrong physical shape: {self._shape}")

        self._mask_size = (2 * int(self._radius) + 1, 2 * int(self._radius) + 1)
        self._mask_center = (int(self._radius), int(self._radius))

    def _get_vertices(self):

        if self._shape == GeometricShapes.RECTANGLE:

            width, length = self._size

            vertices = [
                pymunk.Vec2d(width / 2.0, length / 2.0),
                pymunk.Vec2d(width / 2.0, -length / 2.0),
                pymunk.Vec2d(-width / 2.0, -length / 2.0),
                pymunk.Vec2d(-width / 2.0, length / 2.0),
            ]

        elif self._shape in [
            GeometricShapes.TRIANGLE,
            GeometricShapes.SQUARE,
            GeometricShapes.PENTAGON,
            GeometricShapes.HEXAGON,
        ]:

            radius = self._radius
            number_sides = self._shape.value
            orig = pymunk.Vec2d(radius, 0)

            vertices = []
            for n_sides in range(number_sides):
                vertices.append(orig.rotated(n_sides * 2 * math.pi / number_sides))

        elif self._shape == GeometricShapes.POLYGON:
            vertices = self._vertices

        elif self._shape == GeometricShapes.CIRCLE:
            return None

        else:
            raise ValueError

        return vertices

    def rotate(self, angle: float):
        self._vertices = self.get_rotated_vertices(angle)

    def get_rotated_vertices(self, angle: float):
        vertices_rotated = []

        for pt in self._vertices:
            pt_rotated = pt.rotated(angle)
            vertices_rotated.append(pt_rotated)

        return vertices_rotated

    def expand(self, additional_length):

        self._radius += additional_length
        self._size = (
            self._size[0] + additional_length,
            self._size[1] + additional_length,
        )

        if self._vertices:
            self._vertices = [
                pymunk.Vec2d(x, y) + pymunk.Vec2d(x, y).normalized() * additional_length
                for x, y in self._vertices
            ]

    def compute_mask(self, angle: Optional[float] = 0):

        if self._shape is GeometricShapes.CIRCLE:
            mask = np.zeros(self._mask_size)
            rr, cc = skimage.draw.disk(self._mask_center, self._radius)
            mask[rr, cc] = 1

        else:
            vertices = self.get_rotated_vertices(angle=angle)
            polygon = np.asarray(vertices)
            polygon += self._mask_center
            mask = skimage.draw.polygon2mask(self._mask_size, polygon=polygon) * 1

        return mask
