import arcade
import pytest

from spg.components.elements.wall import ColorWall, TiledAlternateColorWall
from spg.core.playground import EmptyPlayground


@pytest.fixture(scope="module", params=[ColorWall, TiledAlternateColorWall])
def wall_cls(request):
    return request.param


@pytest.fixture(
    scope="module",
    params=[None, arcade.color.REDWOOD, arcade.color.YELLOW, arcade.color.BLUE],
)
def wall_color(request):
    return request.param


@pytest.fixture(scope="module", params=[5, 10, 32, 40])
def wall_width(request):
    return request.param


def test_wall_size(wall_cls, wall_color, wall_width):

    playground = EmptyPlayground(size=(100, 100), background=(23, 23, 21))

    wall = wall_cls((-10, -10), (-10, 90), wall_width=wall_width, color=wall_color)
    playground.add(wall, wall.wall_coordinates)

    assert wall.width == wall_width
    assert wall.height == 100
    assert wall.position == (-10, 40)
