import arcade.color
import numpy as np
import pytest

from spg.core.playground import EmptyPlayground
from spg.core.view import View
from tests.mock_entities import DynamicElementFromGeometry, StaticElementFromGeometry

coord_center = (0, 0), 0
coord_shifted_center = (0, 5), 0


# from spg import Playground
# from spg.view import TopDownView
# from tests.mock_entities import (
#     MockPhysicalFromShape,
#     MockPhysicalInteractive,
#     MockPhysicalMovable,
#     MockPhysicalUnmovable,
#     MockZoneInteractive,
# )


@pytest.mark.parametrize("view_size", [(300, 300), (100, 100)])
@pytest.mark.parametrize("color_bg", [(0, 0, 0), (255, 255, 255), arcade.color.COAL])
@pytest.mark.parametrize("center", [(0, 0), (100, 100)])
@pytest.mark.parametrize("scale", [0.5, 1, 2, 3])
def test_empty_pg(view_size, color_bg, center, scale):
    """Tests that background is set correctly"""

    playground = EmptyPlayground(background=color_bg, size=(100, 100))
    view = View(playground, size_on_playground=view_size, center=center, scale=scale)

    np_img = view.get_np_img()
    assert np.all(np_img[0, 0] == color_bg)

    assert np_img.shape[1] == view_size[1] * scale
    assert np_img.shape[0] == view_size[0] * scale


def test_non_empty_pg():
    playground = EmptyPlayground(size=(100, 100))
    view = View(playground, size_on_playground=(100, 100), center=(0, 0), scale=1)

    ent_1 = StaticElementFromGeometry(geometry="circle", radius=10, color=(0, 0, 255))
    playground.add(ent_1, coord_center)

    np_img = view.get_np_img()
    assert np.sum(np_img) > 0


@pytest.mark.parametrize(
    "color",
    [
        arcade.color.CHOCOLATE,
        arcade.color.RED,
        arcade.color.BLUE,
        arcade.color.GREEN,
        arcade.color.BLACK,
        arcade.color.WHITE,
    ],
)
@pytest.mark.parametrize("center_view", [(-100, -100), (100, 100)])
@pytest.mark.parametrize(
    "color_bg", [arcade.color.YELLOW, arcade.color.WHITE, arcade.color.BLACK]
)
def test_entity_size(color, color_bg, center_view):
    playground = EmptyPlayground(size=(400, 400), background=color_bg)

    view_1 = View(
        playground, size_on_playground=(400, 400), center=center_view, scale=1
    )

    ent_1 = StaticElementFromGeometry(geometry="circle", radius=10, color=color)
    playground.add(ent_1, coord_center)

    view_2 = View(playground, size_on_playground=(400, 400), center=(0, 0), scale=1)

    assert len(view_1.entity_to_sprites) == 1
    assert len(view_2.entity_to_sprites) == 1

    assert len(view_1.scene.get_sprite_list("entity")) == 1
    assert len(view_2.scene.get_sprite_list("entity")) == 1

    img_1 = view_1.get_np_img()
    img_2 = view_2.get_np_img()

    assert np.all(img_1[200, 200] == color_bg)
    assert np.all(img_2[200, 200] == color)

    assert np.all(img_2[200 - center_view[0], 200 - center_view[1]] == color_bg)
    assert np.all(img_1[200 - center_view[0], 200 - center_view[1]] == color)


def test_traversable():
    color_1 = (1, 2, 3)
    color_2 = (2, 3, 4)
    color_3 = (3, 4, 5)

    playground = EmptyPlayground(size=(400, 400))

    ent_1 = DynamicElementFromGeometry(geometry="circle", radius=10, color=color_1)
    playground.add(ent_1, coord_center)

    traversable = DynamicElementFromGeometry(
        geometry="circle", radius=10, traversable=True, color=color_2
    )
    playground.add(traversable, coord_center)

    ent_2 = StaticElementFromGeometry(geometry="circle", radius=10, color=color_3)
    playground.add(ent_2, coord_center)

    view = View(playground, size_on_playground=(400, 400), center=(0, 0), scale=1)

    assert len(view.entity_to_sprites) == 3
    assert len(view.scene.get_sprite_list("entity")) == 2
    assert len(view.scene.get_sprite_list("traversable")) == 1
    assert traversable.traversable

    img = view.get_np_img()

    assert np.all(img[200, 200] == color_2)


@pytest.mark.parametrize("draw_transparent", [True, False])
def test_transparent(draw_transparent):
    color_1 = (50, 50, 100)
    color_2 = (50, 199, 30)

    playground = EmptyPlayground(size=(400, 400))

    ent_1 = DynamicElementFromGeometry(geometry="circle", radius=10, color=color_1)
    playground.add(ent_1, coord_center)

    transparent = DynamicElementFromGeometry(
        geometry="circle", radius=10, transparent=True, color=color_2
    )
    playground.add(transparent, coord_shifted_center)

    view = View(
        playground,
        size_on_playground=(400, 400),
        center=(0, 0),
        scale=1,
        draw_transparent=draw_transparent,
    )

    assert len(view.entity_to_sprites) == 1 + int(draw_transparent)
    assert len(view.scene.get_sprite_list("entity")) == 1 + int(draw_transparent)
    assert transparent.transparent

    img = view.get_np_img()

    assert np.any(img[200, 200] == color_1)


def test_remove_entity():
    playground = EmptyPlayground(size=(400, 400))

    ent_1 = DynamicElementFromGeometry(geometry="circle", radius=10, color=(1, 2, 3))
    playground.add(ent_1, coord_center)

    view = View(playground, size_on_playground=(400, 400), center=(0, 0), scale=1)

    img = view.get_np_img()

    playground.remove(ent_1)

    view.update(force=True)
    img_2 = view.get_np_img()

    assert not np.all(img == img_2)


def test_move_entity():

    playground = EmptyPlayground(size=(400, 400))

    ent_1 = DynamicElementFromGeometry(geometry="circle", radius=10, color=(1, 2, 3))
    playground.add(ent_1, coord_center)

    view = View(playground, size_on_playground=(400, 400), center=(0, 0), scale=1)

    img = view.get_np_img()

    ent_1.move_to(coord_shifted_center)

    view.update(force=True)
    img_2 = view.get_np_img()

    assert not np.all(img == img_2)
    assert np.sum(img) == np.sum(img_2)


def test_reset_playground():

    playground = EmptyPlayground(size=(400, 400))

    ent_1 = DynamicElementFromGeometry(geometry="circle", radius=10, color=(1, 2, 3))
    playground.add(ent_1, coord_center)

    view = View(playground, size_on_playground=(400, 400), center=(0, 0), scale=1)

    img = view.get_np_img()

    playground.reset()

    view.update(force=True)
    img_2 = view.get_np_img()

    assert not np.all(img == img_2)
    assert not np.sum(img) == np.sum(img_2)
