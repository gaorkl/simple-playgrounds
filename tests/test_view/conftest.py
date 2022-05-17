import pytest
import math
import arcade.color as color

@pytest.fixture(scope="module", params=[5, 10, 21])
def radius(request):
    return request.param


@pytest.fixture(scope="module", params=[(0, 0), (50, 50), (-50, -50)])
def position(request):
    return request.param


@pytest.fixture(scope="module", params=[(0, 0), (30, -30), ( -30, 30)])
def center(request):
    return request.param


@pytest.fixture(scope="module", params=[0, math.pi/7, math.pi/4])
def angle(request):
    return request.param


@pytest.fixture(scope="module", params=['circle', 'square', 'pentagon', 'triangle', 'hexagon'])
def shape(request):
    return request.param


@pytest.fixture(scope="module", params=['square', 'pentagon', 'triangle', 'hexagon'])
def poly_shape(request):
    return request.param


@pytest.fixture(scope="module", params=[1, 0.5, 2])
def zoom(request):
    return request.param


@pytest.fixture(scope="module", params=[(50, 50), (150, 150)])
def view_size(request):
    return request.param


@pytest.fixture(scope="module", params=[color.BLACK, color.WHITE, color.ORANGE, color.AMARANTH, (255, 0, 0)])
def color_bg(request):
    return request.param



