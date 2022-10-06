import arcade
import pytest

from spg.element import ColorWall, TiledAlternateColorWall
from spg.playground import Playground


@pytest.fixture(scope="module", params=[ColorWall, TiledAlternateColorWall])
def wall_cls(request):
    return request.param


@pytest.fixture(
    scope="module", params=[None, arcade.color.REDWOOD, (10, 20, 30), [10, 23, 43]]
)
def wall_color(request):
    return request.param


@pytest.fixture(scope="module", params=[5, 10, 32, 40])
def wall_width(request):
    return request.param


def test_wall_size(wall_cls, wall_color, wall_width):

    playground = Playground()

    wall = wall_cls((-10, -10), (-10, 90), wall_width, wall_color)
    playground.add(wall, wall.wall_coordinates)

    assert wall.width == wall_width
    assert wall.length == 100
    assert wall.position == (-10, 40)
