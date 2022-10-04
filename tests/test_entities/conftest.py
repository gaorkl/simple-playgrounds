import pytest


@pytest.fixture(scope="module", params=["circle", "square", "rectangle", "polygon"])
def shape(request):
    return request.param


@pytest.fixture(scope="module", params=[5, 10, 20])
def radius(request):
    return request.param


@pytest.fixture(scope="module", params=[(5, 3), (10, 5)])
def size(request):
    return request.param


@pytest.fixture(
    scope="module",
    params=[
        ((-5, -5), (5, -5), (10, 0)),
        ((-5, -5), (5, -5), (5, 10), (-10, 5)),
    ],
)
def vertices(request):
    return request.param


@pytest.fixture(scope="module", params=[5, 10])
def interaction_radius(request):
    return request.param
