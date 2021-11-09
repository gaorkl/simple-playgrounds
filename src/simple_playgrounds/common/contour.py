from typing import Optional, Tuple, List
from collections import namedtuple
from enum import IntEnum, auto

import numpy as np
import math
import pymunk

Contour = namedtuple('Contour', 'shape radius size vertices')


class GeometricShapes(IntEnum):
    LINE = 2
    TRIANGLE = 3
    SQUARE = 4
    PENTAGON = 5
    HEXAGON = 6
    CIRCLE = 60
    RECTANGLE = auto()
    POLYGON = auto()


def get_contour(geometric_shape: str,
                radius: Optional[float] = None,
                size: Optional[Tuple[float, float]] = None,
                vertices: Optional[List[Tuple[float, float]]] = None,
                **kwargs):

    geometric_shape = GeometricShapes[geometric_shape.upper()]

    assert geometric_shape in [i for i in GeometricShapes]

    # Dimensions of the entity

    if geometric_shape in [
        GeometricShapes.TRIANGLE,
        GeometricShapes.SQUARE,
        GeometricShapes.PENTAGON,
        GeometricShapes.HEXAGON,
        GeometricShapes.CIRCLE,
    ]:
        assert radius is not None and isinstance(radius, (float, int))

        radius = radius
        size = (2 * radius, 2 * radius)

    elif geometric_shape == GeometricShapes.RECTANGLE:
        assert size is not None and len(size) == 2

        width, length = size
        radius = ((width / 2) ** 2 + (length / 2) ** 2) ** (1 / 2)
        size = size

    elif geometric_shape == GeometricShapes.POLYGON:
        assert vertices and len(vertices) > 1

        vertices = np.array(vertices)
        center = np.mean(vertices, axis=0)
        vertices = vertices - center

        width = np.max(vertices[:, 0]) - np.min(vertices[:, 0])
        length = np.max(vertices[:, 1]) - np.min(vertices[:, 1])

        radius = ((width / 2) ** 2 + (length / 2) ** 2) ** (1 / 2)
        size = (2 * radius, 2 * radius)

    else:
        raise ValueError('Wrong physical shape: {}.'.format(geometric_shape))

    contour = Contour(geometric_shape, radius, size, vertices)

    # compute missing vertices
    vertices = get_vertices(contour)
    contour = Contour(geometric_shape, radius, size, vertices)

    return contour


def get_vertices(contour: Contour, offset_angle=0.):

    vertices = []

    if contour.shape == GeometricShapes.RECTANGLE:

        width, length = contour.size

        points = [
            pymunk.Vec2d(width / 2., length / 2.),
            pymunk.Vec2d(width / 2., -length / 2.),
            pymunk.Vec2d(-width / 2., -length / 2.),
            pymunk.Vec2d(-width / 2., length / 2.)
        ]

    elif contour.shape in [
        GeometricShapes.TRIANGLE,
        GeometricShapes.SQUARE,
        GeometricShapes.PENTAGON,
        GeometricShapes.HEXAGON,
    ]:

        radius = contour.radius
        number_sides = contour.shape.value
        orig = pymunk.Vec2d(radius, 0)

        points = []
        for n_sides in range(number_sides):
            points.append(
                orig.rotated(n_sides * 2 * math.pi / number_sides))

    elif contour.shape == GeometricShapes.POLYGON:
        points = contour.vertices

    elif contour.shape == GeometricShapes.CIRCLE:
        return None

    else:
        raise ValueError

    for pt in points:
        pt_rotated = pt.rotated(offset_angle)
        vertices.append(pt_rotated)

    return vertices


def expand_contour(contour: Contour, additional_length):

    radius = contour.radius + additional_length
    size = contour.size[0] + additional_length, contour.size[1] + additional_length

    vertices = None
    if contour.vertices:
        vertices = [pymunk.Vec2d(x, y) + pymunk.Vec2d(x, y).normalized() * additional_length for x, y in
                    contour.vertices]

    return Contour(contour.shape, radius, size, vertices)