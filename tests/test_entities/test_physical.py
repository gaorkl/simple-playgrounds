from typing import Optional

import numpy as np

from simple_playgrounds.playground.playground import EmptyPlayground


def test_traversable_traversable(physical_traversable, physical_traversable_2):

    playground = EmptyPlayground()

    # Two traversable shouldn't collide with either traversables or non-traversables
    playground.add(physical_traversable, ((10, 10), 0))
    playground.add(physical_traversable_2, ((10, 10), 0))

    playground.update()
    assert physical_traversable.position == physical_traversable_2.position


def test_traversable_basic(physical_traversable, physical_basic):

    playground = EmptyPlayground()

    playground.add(physical_traversable, ((10, 10), 0))
    playground.add(physical_basic, ((10, 10), 0))

    playground.update()
    assert physical_traversable.position == physical_basic.position


def test_basic_basic(physical_basic, physical_basic_2):
    playground = EmptyPlayground()

    playground.add(physical_basic, ((10, 10), 0))
    playground.add(physical_basic_2, ((10, 10), 0))

    playground.update()
    assert physical_basic.position != physical_basic_2.position


def test_transparent(physical_transparent):
    playground = EmptyPlayground()
    view_empty = playground.view((0, 0), (50, 50))

    playground.add(physical_transparent, ((10, 10), 0))
    view_transparent = playground.view((0, 0), (50, 50))
    assert np.all(view_transparent == view_empty)

    view_transparent_visible = playground.view((0, 0), (50, 50), draw_invisible=True)
    assert not np.all(view_transparent == view_transparent_visible)



# def test_non_traversable():
#
#     playground = EmptyPlayground()
#
#     contour = Contour('circle', 10, None, None)
#
#     # Two traversable shouldn't collide with either traversables or non-traversables
#     physical_1 = TestEntity(traversable=True, transparent=False, **contour._asdict(), texture=(10, 100, 100))
#     playground.add(traversable_1, ((10, 10), 0))
#
#     traversable_2 = TestEntity(traversable=True, transparent=False, **contour._asdict(), texture=(10, 100, 100))
#     playground.add(traversable_2, ((10, 10), 0))