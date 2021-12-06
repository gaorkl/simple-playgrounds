import pytest

from simple_playgrounds.common.contour import Contour


@pytest.fixture(scope="module", params=['square', 'triangle', 'hexagon', 'pentagon'])
def shape(request):
    return request.param


@pytest.fixture(scope="module", params=[5, 10, 20])
def radius(request):
    return request.param
