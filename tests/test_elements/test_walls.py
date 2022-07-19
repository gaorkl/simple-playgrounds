from simple_playgrounds.playground.playground import EmptyPlayground
from simple_playgrounds.element.basic.wall import (
    ColorWall,
    create_wall_from_blocks,
    BrickWallBlock,
)
from simple_playgrounds.common.view import TopDownView
from simple_playgrounds.playground.playgrounds.simple import WallClosedPG


def test_wall_size():

    playground = EmptyPlayground()

    wall = ColorWall(playground, (-10, -10), (-10, 90), 20, (255, 0, 0))

    assert wall.width == 20
    assert wall.length == 100 + 20

    view = TopDownView(playground, center=(0, 0), size=(400, 400), zoom=1)

    assert wall.position == (-10, 40)


def test_wall_blocks():

    playground = EmptyPlayground()

    create_wall_from_blocks(playground, BrickWallBlock, (-150, -150), (150, 150), 50)
    create_wall_from_blocks(playground, BrickWallBlock, (-150, -150), (-150, 150), 50)

    view = TopDownView(playground, center=(0, 0), size=(400, 400), zoom=1)


def test_wall_room():

    playground = WallClosedPG(size=(400, 200), background=(10, 134, 200))

    view = TopDownView(playground, center=(0, 0), size=(400, 200), zoom=1)

