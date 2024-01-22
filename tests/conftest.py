import gc

import pytest

from spg.core.playground import Playground

###########################
# ENTITY PROPERTIES
###########################


@pytest.fixture(scope="session", params=["segment", "circle", "square"])
def geometry(request):
    return request.param


@pytest.fixture(scope="session", params=["circle", "box", "decomposition", None])
def shape_approx(request):
    return request.param


@pytest.fixture(scope="session", params=[0, 50, 150])
def comm_radius(request):
    return request.param


@pytest.fixture(scope="session", autouse=True)
def dummy_pg():
    print(gc.get_objects())
    return Playground(size=(100, 100))
