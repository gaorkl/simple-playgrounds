import math
import numpy as np

from spg.playground import Playground
from spg.view import TopDownView
from ..mock_entities import (
    MockPhysicalFromShape,
    MockPhysicalInteractive,
    MockPhysicalMovable,
    MockPhysicalUnmovable,
    MockZoneInteractive,
)

center_view = (0, 0)


def test_empty_pg(view_size, zoom, color_bg):
    """Tests that background is set correctly"""

    playground = Playground(background=color_bg)
    view = TopDownView(playground, center=center_view, size=view_size, zoom=zoom)

    view.update()

    assert np.all(view.get_np_img()[0, 0] == color_bg)
    # assert view.img.shape == (*view_size, 3)


def test_shape(geometry, position, center):

    color_ent = (123, 122, 54)
    playground = Playground()
    ent_1 = MockPhysicalFromShape(geometry=geometry, size=10, color=color_ent)
    playground.add(
        ent_1,
        (position, math.pi / 3),
    )

    view = TopDownView(playground, center=center, size=(300, 300), display_uid=False)

    view.update()

    ent_pos_on_image = (150 + position[0] + center[0], 150 + position[1] + center[1])

    assert np.all(
        view.get_np_img()[ent_pos_on_image[0], ent_pos_on_image[1]] == color_ent
    )


def test_position(geometry, position, zoom):

    color_ent = (123, 122, 54)
    playground = Playground()
    ent_1 = MockPhysicalFromShape(geometry=geometry, size=10, color=color_ent)
    playground.add(
        ent_1,
        (position, math.pi / 3),
    )

    view = TopDownView(
        playground, zoom=zoom, center=center_view, size=(300, 300), display_uid=False
    )

    view.update()

    ent_pos_on_image = (150 + int(position[0] * zoom), 150 + int(position[1] * zoom))

    # print(position)
    # print(center)
    # view.imdisplay()
    # assert np.all(view.img[0, 0] == color_bg)
    assert np.all(
        view.get_np_img()[ent_pos_on_image[0], ent_pos_on_image[1]] == color_ent
    )


def test_traversable(geometry, position, zoom):

    color_1 = (123, 122, 54)
    color_2 = (13, 12, 54)

    playground = Playground()
    ent_1 = MockPhysicalFromShape(
        geometry=geometry,
        size=10,
        color=color_1,
        traversable=True,
    )
    playground.add(
        ent_1,
        (position, math.pi / 3),
    )

    ent_2 = MockPhysicalFromShape(geometry=geometry, size=10, color=color_2)
    playground.add(
        ent_2,
        (position, math.pi / 3),
    )

    view = TopDownView(
        playground, zoom=zoom, center=center_view, size=(300, 300), display_uid=False
    )

    view.update()

    ent_pos_on_image = (150 + int(position[0] * zoom), 150 + int(position[1] * zoom))

    # print(position)
    # print(center)
    # view.imdisplay()
    # assert np.all(view.img[0, 0] == color_bg)
    assert np.all(
        view.get_np_img()[ent_pos_on_image[0], ent_pos_on_image[1]] == color_1
    )


def test_transparent(geometry, position, zoom):

    color_1 = (123, 122, 54)
    color_2 = (13, 12, 54)

    playground = Playground()
    ent_1 = MockPhysicalFromShape(
        geometry=geometry,
        size=10,
        color=color_1,
        transparent=True,
    )
    playground.add(
        ent_1,
        (position, math.pi / 3),
    )

    view = TopDownView(
        playground,
        zoom=zoom,
        center=center_view,
        size=(300, 300),
        display_uid=False,
        draw_transparent=False,
    )

    view.update()

    ent_pos_on_image = (150 + int(position[0] * zoom), 150 + int(position[1] * zoom))

    # print(position)
    # print(center)
    # view.imdisplay()
    # assert np.all(view.img[0, 0] == color_bg)
    assert np.all(
        view.get_np_img()[ent_pos_on_image[0], ent_pos_on_image[1]] == (0, 0, 0)
    )


def test_remove_entity():

    color_ent = (123, 122, 54)
    playground = Playground()
    ent_1 = MockPhysicalInteractive(interaction_range=5)
    playground.add(ent_1, ((0, 0), 0))

    view = TopDownView(
        playground,
        zoom=1,
        center=center_view,
        size=(300, 300),
        display_uid=False,
        draw_interactive=True,
    )

    view.update()

    ent_pos_on_image = (150, 150)

    assert not np.all(
        view.get_np_img()[ent_pos_on_image[0], ent_pos_on_image[1]] == (0, 0, 0)
    )

    playground.remove(ent_1)
    assert ent_1 not in view._sprites

    view.update()

    assert np.all(
        view.get_np_img()[ent_pos_on_image[0], ent_pos_on_image[1]] == (0, 0, 0)
    )

    playground.reset()

    view.update()

    assert not np.all(
        view.get_np_img()[ent_pos_on_image[0], ent_pos_on_image[1]] == (0, 0, 0)
    )


def test_move_entity():

    color_ent = (123, 122, 54)
    playground = Playground()
    ent_1 = MockPhysicalFromShape(geometry="circle", size=10, color=color_ent)
    playground.add(ent_1, ((0, 0), 0))

    view = TopDownView(
        playground, zoom=1, center=center_view, size=(300, 300), display_uid=False
    )

    view.update()

    ent_pos_on_image = (150, 150)

    assert np.all(
        view.get_np_img()[ent_pos_on_image[0], ent_pos_on_image[1]] == color_ent
    )

    ent_1.move_to(((100, 100), 0))

    view.update()

    assert np.all(
        view.get_np_img()[ent_pos_on_image[0], ent_pos_on_image[1]] == (0, 0, 0)
    )
    assert np.all(
        view.get_np_img()[ent_pos_on_image[0] + 100, ent_pos_on_image[1] + 100]
        == color_ent
    )


def test_multiple_views():

    color_ent = (123, 122, 54)
    playground = Playground()
    ent_1 = MockPhysicalFromShape(geometry="circle", size=10, color=color_ent)

    playground.add(ent_1, ((0, 0), 0))

    view_2 = TopDownView(
        playground,
        zoom=1,
        center=center_view,
        size=(300, 300),
        display_uid=False,
    )

    view_1 = TopDownView(
        playground,
        zoom=1,
        center=center_view,
        size=(300, 300),
        display_uid=False,
    )

    view_1.update()
    view_2.update()

    assert np.all(view_1.get_np_img() == view_2.get_np_img())

    ent_1.move_to(((10, 10), 0))

    view_1.update()
    assert not np.all(view_1.get_np_img() == view_2.get_np_img())

    view_2.update()

    assert np.all(view_1.get_np_img() == view_2.get_np_img())


def test_visual_view(zoom):

    playground = Playground(background=(123, 0, 134))

    # Position and orientation
    playground.add(MockPhysicalMovable(), ((-100, 100), 0))
    playground.add(MockPhysicalMovable(), ((0, 100), math.pi / 4))
    playground.add(MockPhysicalMovable(), ((100, 100), math.pi / 3))

    # Radius
    playground.add(MockPhysicalMovable(), ((-100, 0), 0))
    playground.add(MockPhysicalMovable(radius=10), ((0, 0), 0))
    playground.add(MockPhysicalMovable(radius=30), ((100, 0), 0))

    # Different shapes
    playground.add(MockPhysicalUnmovable(), ((-100, -100), 0))
    playground.add(MockPhysicalInteractive(interaction_range=10), ((0, -100), 0))
    playground.add(MockZoneInteractive(), ((100, -100), 0))

    # MockPhysicalUnmovable(playground, ((0, 100), 0))

    view = TopDownView(
        playground,
        zoom=zoom,
        center=center_view,
        size=(300, 300),
        display_uid=False,
    )

    view.update()
