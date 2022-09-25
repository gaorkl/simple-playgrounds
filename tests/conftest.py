import pytest

###########################
# ENTITY PROPERTIES
###########################


@pytest.fixture(scope="module", params=[1, 5, 10, 20])
def radius(request):
    return request.param


@pytest.fixture(scope="module", params=["segment", "circle", "square"])
def geometry(request):
    return request.param


@pytest.fixture(scope="module", params=["circle", "box", "decomposition", None])
def shape_approx(request):
    return request.param


@pytest.fixture(scope="module", params=[0, 50, 150])
def comm_radius(request):
    return request.param
