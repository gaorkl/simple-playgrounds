import pytest

from simple_playgrounds.engine import Engine
from simple_playgrounds.playground.layouts import GridRooms, LineRooms, SingleRoom


def test_grid_layout():

    playground = GridRooms(size=(200, 400), room_layout=(4, 2), doorstep_size=50)
    playground = GridRooms(size=(200, 400), random_doorstep_position=True, room_layout=(4, 2), doorstep_size=50)

    with pytest.raises(ValueError):
        playground = GridRooms(size=(200, 400), room_layout=(4, 2), doorstep_size=100)

    with pytest.raises(ValueError):
        playground = GridRooms(size=(200, 400), room_layout=(4, 2), random_doorstep_position=True, doorstep_size=100)

    with pytest.raises(ValueError):
        playground = GridRooms(size=(200, 400), room_layout=(4, 2), doorstep_size=100)

    with pytest.raises(ValueError):
        playground = GridRooms(size=(200, 400), room_layout=(4, 2), random_doorstep_position=True, doorstep_size=100)


def test_playground_textures(wall_type):

    for doorstep_size in [10, 20, 75]:
        playground = GridRooms(size=(450, 300), room_layout=(3, 2), doorstep_size=doorstep_size, wall_type=wall_type)
        playground = GridRooms(size=(450, 300), room_layout=(3, 2), random_doorstep_position=True,
                               doorstep_size=doorstep_size, wall_type=wall_type)
    #
    # with pytest.raises(ValueError):
    #     playground = GridRooms(size=(450, 300), room_layout=(3, 2), doorstep_size=85, wall_type=wall_type)
    #
    # with pytest.raises(ValueError):
    #     playground = GridRooms(size=(450, 300), room_layout=(3, 2), doorstep_size=80, wall_type=wall_type)


def test_line_layout():
    playground = LineRooms(size=(300, 100), number_rooms=3, doorstep_size=50)
    playground = LineRooms(size=(300, 100), number_rooms=1, doorstep_size=50)

    with pytest.raises(ValueError):
        playground = LineRooms(size=(300, 100), number_rooms=5, doorstep_size=50)
