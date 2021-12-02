import random

import pytest

import numpy as np
import math

from simple_playgrounds.playground.playground import EmptyPlayground
from simple_playgrounds.common.view import FixedGlobalView
from simple_playgrounds.common.contour import Contour

from ..mock_entities import MockPhysical


@pytest.fixture(scope="module", params=[3, 10])
def radius(request):
    return request.param


@pytest.fixture(scope="module", params=[(0, 0)])#, (10, 10), (-10, 10)])
def position(request):
    return request.param


@pytest.fixture(scope="module", params=[0, math.pi/3])
def angle(request):
    return request.param


@pytest.fixture(scope="module", params=['circle', 'square', 'pentagon', 'triangle', 'hexagon'])
def shape(request):
    return request.param


@pytest.fixture(scope="module", params=[(10, 10), (13, 13)])
def size_on_pg(request):
    return request.param


@pytest.fixture(scope="module", params=[(20, 20)])
def view_size(request):
    return request.param


def test_view_symmetric(shape, position, angle, radius, size_on_pg, view_size):

    playground = EmptyPlayground()
    view = FixedGlobalView(playground=playground, size_on_playground=size_on_pg, view_size=view_size,
                                 coordinates=((0, 0), 0))

    contour = Contour(shape=shape, radius=radius)
    ent_1 = MockPhysical(contour=contour, transparent=True, movable=True, mass=5)

    playground.add(ent_1, (position, angle))

    img = view.update_view()

    for angle_rot in range(contour.shape.value):
        ent_1.move_to((position, angle_rot*math.pi*2/contour.shape.value))
        img_rotated = view.update_view()

        print(img[:, :, 0])
        print(img_rotated[:, :, 0])

        assert np.all(img_rotated == img)


def test_view_random_rotation(shape, position, angle, radius, size_on_pg, view_size):

    playground = EmptyPlayground()
    view = FixedGlobalView(playground=playground, size_on_playground=size_on_pg, view_size=view_size,
                           coordinates=((0, 0), 0))

    contour = Contour(shape=shape, radius=radius)
    ent_1 = MockPhysical(contour=contour, transparent=True, movable=True, mass=5)

    playground.add(ent_1, (position, angle))

    img = view.update_view()

    for angle_rot in [random.uniform(-1, 1) for _ in range(5)]:
        ent_1.move_to((position, math.pi * 2 / angle_rot))
        img_rotated = view.update_view()

        if radius == 30:
            print(img[:, :, 0])
            print(img_rotated[:, :, 0])

        assert np.any(img_rotated != img)
