import random

import pytest

import numpy as np
import math
from matplotlib.colors import to_rgb

from simple_playgrounds.playground.playground import EmptyPlayground
from simple_playgrounds.common.view import FixedGlobalView
from simple_playgrounds.common.contour import Contour

from ..mock_entities import MockPhysical


@pytest.fixture(scope="module", params=[5, 10, 21])
def radius(request):
    return request.param


@pytest.fixture(scope="module", params=[(0, 0), (20, 20), (-20, 20)])
def position(request):
    return request.param


@pytest.fixture(scope="module", params=[0, math.pi/7])
def angle(request):
    return request.param


@pytest.fixture(scope="module", params=['circle', 'square', 'pentagon', 'triangle', 'hexagon'])
def shape(request):
    return request.param


@pytest.fixture(scope="module", params=[(100, 100)])
def size_on_pg(request):
    return request.param


@pytest.fixture(scope="module", params=[(13, 13), (16, 16)])
def view_size(request):
    return request.param


@pytest.fixture(scope="module", params=['black', 'white', 'orange', 'purple', 'grey'])
def color_bg(request):
    return request.param


def test_empty_pg(size_on_pg, color_bg):
    """ Tests that background is set correctly """

    playground = EmptyPlayground()
    view = FixedGlobalView(playground=playground, size_on_playground=size_on_pg,
                           coordinates=((0, 0), 0), background_color=color_bg)

    img = view.update_view()
    assert np.all(img[0, 0]/255 == to_rgb(color_bg))


def test_add_big_shape(size_on_pg, color_bg):

    playground = EmptyPlayground()
    view = FixedGlobalView(playground=playground, size_on_playground=size_on_pg,
                           coordinates=((0, 0), 0), background_color=color_bg)

    contour = Contour(shape='circle', radius=size_on_pg[0]*2)
    ent_1 = MockPhysical(contour=contour, transparent=True, movable=True, mass=5)
    playground.add(ent_1, ((0, 0), 0))

    img = view.update_view()

    assert np.all(img[0, 0] == ent_1.base_color)


def test_view_symmetric(shape, position, angle, radius, size_on_pg):
    """ Rotating elements by the correct angle should lead to the same image """

    playground = EmptyPlayground()
    view = FixedGlobalView(playground=playground, size_on_playground=size_on_pg,
                                 coordinates=((0, 0), 0))

    contour = Contour(shape=shape, radius=radius)
    ent_1 = MockPhysical(contour=contour, transparent=True, movable=True, mass=5)

    playground.add(ent_1, (position, angle))

    img = view.update_view()

    for angle_rot in range(contour.shape.value):
        ent_1.move_to((position, angle + angle_rot*math.pi*2/contour.shape.value))
        img_rotated = view.update_view()

        assert np.all(img_rotated == img)


def test_view_random_rotation(shape, position, angle, radius, size_on_pg):
    """ Rotating elements by the correct angle should lead to the different image """

    playground = EmptyPlayground()
    view = FixedGlobalView(playground=playground, size_on_playground=size_on_pg,
                           coordinates=((0, 0), 0))

    contour = Contour(shape=shape, radius=radius)
    ent_1 = MockPhysical(contour=contour, transparent=True, movable=True, mass=5)

    playground.add(ent_1, (position, angle))
    img = view.update_view()

    angle_rot = math.pi / contour.shape.value

    ent_1.move_to((position,  angle_rot))
    img_rotated = view.update_view()

    if shape != 'circle':
        assert np.any(img_rotated != img)
