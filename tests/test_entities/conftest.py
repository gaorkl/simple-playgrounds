import pytest

from simple_playgrounds.entity.contour import Contour


@pytest.fixture(scope="module", params=['circle', 'square', 'rectangle', 'polygon'])
def shape(request):
    return request.param


@pytest.fixture(scope="module", params=[5, 10, 20])
def radius(request):
    return request.param


@pytest.fixture(scope="module", params=[(5, 3), (10, 5)])
def size(request):
    return request.param


@pytest.fixture(scope="module", params=[
    ((-5, -5), (5, -5), (10, 0)),
    ((-5, -5), (5, -5), (5, 10), (-10, 5)),
])
def vertices(request):
    return request.param


@pytest.fixture(scope="function")
def custom_contour(shape, radius, size, vertices):
    return Contour(shape=shape, radius=radius, size=size, vertices=vertices)


custom_contour_2 = custom_contour


@pytest.fixture(scope="module", params=[5, 10])
def interaction_radius(request):
    return request.param
