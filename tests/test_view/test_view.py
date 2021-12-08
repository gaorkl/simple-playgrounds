import random
import math

import pytest

import numpy as np
from matplotlib.colors import to_rgb
from skimage import transform

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


@pytest.fixture(scope="module", params=[(100, 100), (300, 300)])
def size_on_pg(request):
    return request.param


@pytest.fixture(scope="module", params=[(50, 50), (150, 150)])
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

# @pytest.fixture()

def test_view_scale(shape, position, angle, radius, size_on_pg, view_size):
    
    playground = EmptyPlayground()
    contour = Contour(shape=shape, radius=radius)
    ent_1 = MockPhysical(contour=contour, transparent=True, movable=True, mass=5)

    playground.add(ent_1, (position, angle))

    view_no_rescale = FixedGlobalView(playground=playground, size_on_playground=size_on_pg,
                           coordinates=((0, 0), 0)).update_view()

    view_rescale = FixedGlobalView(playground=playground, size_on_playground=size_on_pg,
                           coordinates=((0, 0), 0), view_size=view_size).update_view()

    assert view_no_rescale.shape == (*size_on_pg, 3)
    assert view_rescale.shape == (*view_size, 3)

    resized_view = transform.resize(view_no_rescale, view_size, anti_aliasing=False, preserve_range=True, order=0)
    
    # Because of approximations when resizing, we approximate also for testing.
    total_pixels_equal = np.sum( ((resized_view == view_rescale) * 
                                 (resized_view != np.zeros(resized_view.shape) )).prod(axis=2))
    total_pixels_resized = np.sum( (resized_view != np.zeros(resized_view.shape)).prod(axis=2))
    total_pixels_rescale = np.sum( (view_rescale != np.zeros(resized_view.shape)).prod(axis=2))
   

    assert resized_view.shape == view_rescale.shape
    if radius > 10:
        assert 2*total_pixels_equal/(total_pixels_rescale + total_pixels_resized) > 0.9
    
