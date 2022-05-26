import math
import numpy as np

from simple_playgrounds.playground.playground import EmptyPlayground
from simple_playgrounds.common.view import TopDownView
from tests.test_view.conftest import color_bg
from ..mock_entities import MockPhysicalFromShape, MockPhysicalInteractive, MockPhysicalMovable, MockPhysicalUnmovable, MockZoneInteractive

center_view = (0, 0)


def test_empty_pg(view_size, zoom, color_bg):
    """ Tests that background is set correctly """

    playground = EmptyPlayground(background=color_bg)
    view = TopDownView(playground, 
                       center = center_view, size = view_size,
                       zoom = zoom)

    view.update()

    assert np.all(view.img[0, 0] == color_bg)
    # assert view.img.shape == (*view_size, 3)


def test_shape( geometry, position, center ):

    color_ent = (123, 122, 54)
    playground = EmptyPlayground()
    ent_1 = MockPhysicalFromShape(playground, (position, math.pi/3), geometry = geometry, size=10, color=color_ent)

    view = TopDownView(playground, 
                       center = center, size = (300, 300), display_uid=False)

    view.update()

    ent_pos_on_image = (150 + position[0] + center[0],
                        150 + position[1] + center[1])

    # print(position)
    # print(center)
    # view.imdisplay()
    # assert np.all(view.img[0, 0] == color_bg)
    assert np.all(view.img[ent_pos_on_image[0], ent_pos_on_image[1]] == color_ent)


def test_position(geometry, position, zoom):
    
    color_ent = (123, 122, 54)
    playground = EmptyPlayground()
    ent_1 = MockPhysicalFromShape(playground, (position, math.pi/3), geometry = geometry, size=10, color=color_ent)

    view = TopDownView(playground, zoom=zoom, 
                       center = center_view, size = (300, 300), display_uid=False)

    view.update()

    ent_pos_on_image = (150 + int(position[0]*zoom),
                        150 + int(position[1]*zoom))

    # print(position)
    # print(center)
    # view.imdisplay()
    # assert np.all(view.img[0, 0] == color_bg)
    assert np.all(view.img[ent_pos_on_image[0], ent_pos_on_image[1]] == color_ent)


def test_traversable(geometry, position, zoom):
    
    color_1 = (123, 122, 54)
    color_2 = (13, 12, 54)

    playground = EmptyPlayground()
    ent_1 = MockPhysicalFromShape(playground, (position, math.pi/3), geometry = geometry, size=10, color=color_1, traversable=True)
    ent_2 = MockPhysicalFromShape(playground, (position, math.pi/3), geometry = geometry, size=10, color=color_2)

    view = TopDownView(playground, zoom=zoom, 
                       center = center_view, size = (300, 300), display_uid=False)

    view.update()

    ent_pos_on_image = (150 + int(position[0]*zoom),
                        150 + int(position[1]*zoom))

    # print(position)
    # print(center)
    # view.imdisplay()
    # assert np.all(view.img[0, 0] == color_bg)
    assert np.all(view.img[ent_pos_on_image[0], ent_pos_on_image[1]] == color_1)


def test_transparent(geometry, position, zoom):
    
    color_1 = (123, 122, 54)
    color_2 = (13, 12, 54)

    playground = EmptyPlayground()
    ent_1 = MockPhysicalFromShape(playground, (position, math.pi/3), geometry = geometry, size=10, color=color_1, transparent=True)

    view = TopDownView(playground, zoom=zoom, 
                       center = center_view, size = (300, 300), display_uid=False, draw_transparent=False)

    view.update()

    ent_pos_on_image = (150 + int(position[0]*zoom),
                        150 + int(position[1]*zoom))

    # print(position)
    # print(center)
    # view.imdisplay()
    # assert np.all(view.img[0, 0] == color_bg)
    assert np.all(view.img[ent_pos_on_image[0], ent_pos_on_image[1]] == (0,0,0))


def test_remove_entity():

    color_ent = (123, 122, 54)
    playground = EmptyPlayground()
    ent_1 = MockPhysicalInteractive(playground, ((0,0), 0), interaction_range=10)

    view = TopDownView(playground, zoom=1, 
                       center = center_view, size = (300, 300), display_uid=False,draw_interactive=True)

    view.update()

    ent_pos_on_image = (150,150)

    assert not np.all(view.img[ent_pos_on_image[0], ent_pos_on_image[1]] == (0,0,0))

    ent_1.remove()

    view.update()

    assert np.all(view.img[ent_pos_on_image[0], ent_pos_on_image[1]] == (0,0,0))

    playground.reset()

    view.update()


    assert not np.all(view.img[ent_pos_on_image[0], ent_pos_on_image[1]] == (0,0,0))

def test_move_entity():

    color_ent = (123, 122, 54)
    playground = EmptyPlayground()
    ent_1 = MockPhysicalFromShape(playground, ((0,0), 0), geometry = 'circle', size=10, color=color_ent)

    view = TopDownView(playground, zoom=1, 
                       center = center_view, size = (300, 300), display_uid=False)

    view.update()

    ent_pos_on_image = (150,150)

    assert np.all(view.img[ent_pos_on_image[0], ent_pos_on_image[1]] == color_ent)

    ent_1.move_to( ((100, 100), 0 ))

    view.update()

    assert np.all(view.img[ent_pos_on_image[0], ent_pos_on_image[1]] == (0,0,0))
    assert np.all(view.img[ent_pos_on_image[0]+100, ent_pos_on_image[1]+100] == color_ent)


def test_multiple_views():

    color_ent = (123, 122, 54)
    playground = EmptyPlayground()
    ent_1 = MockPhysicalFromShape(playground, ((0,0), 0), geometry = 'circle', size=10, color=color_ent)

    view_1 = TopDownView(playground, zoom=1, 
                       center = center_view, size = (300, 300), display_uid=False)

    view_2 = TopDownView(playground, zoom=1, 
                       center = center_view, size = (300, 300), display_uid=False)
    view_1.update()
    view_2.update()

    assert np.all(view_1.img == view_2.img)

    ent_1.move_to( ((10, 10), 0 ))

    view_1.update()
    assert not np.all(view_1.img == view_2.img)

    view_2.update()

    assert np.all(view_1.img == view_2.img)


def test_visual_view(zoom):

    playground = EmptyPlayground(background= (123, 0, 134))
   
    # Position and orientation
    MockPhysicalMovable(playground, ((-100, 100), 0))
    MockPhysicalMovable(playground, ((0, 100), math.pi/4))
    MockPhysicalMovable(playground, ((100, 100), math.pi/3))
    
    # Radius
    MockPhysicalMovable(playground, ((-100, 0), 0))
    MockPhysicalMovable(playground, ((0, 0), 0), radius = 10)
    MockPhysicalMovable(playground, ((100, 0), 0), radius = 30)

    # Different shapes
    MockPhysicalUnmovable(playground, ((-100, -100), 0))
    MockPhysicalInteractive(playground, ((0, -100), 0), interaction_range=10)
    MockZoneInteractive(playground, ((100, -100), 0))

    # MockPhysicalUnmovable(playground, ((0, 100), 0))

    view = TopDownView(playground, zoom=zoom, 
                       center = center_view, size = (300, 300), display_uid=False)

    view.update()

    view.imdisplay()
