import pytest
import math


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



