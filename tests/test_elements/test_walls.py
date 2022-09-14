from spg.element import BrickWallBlock, ColorWall, create_wall_from_blocks
from spg.playground import Playground, WallClosedPG


def test_wall_size():

    playground = Playground()

    wall = ColorWall((-10, -10), (-10, 90), 20, (255, 0, 0))
    playground.add(wall, wall.wall_coordinates)

    assert wall.width == 20
    assert wall.length == 100 + 20
    assert wall.position == (-10, 40)


def test_wall_blocks():

    playground = Playground()

    create_wall_from_blocks(playground, BrickWallBlock, (-150, -150), (150, 150), 50)
    create_wall_from_blocks(playground, BrickWallBlock, (-150, -150), (-150, 150), 50)


def test_wall_room():

    WallClosedPG(size=(400, 200), background=(10, 134, 200))
