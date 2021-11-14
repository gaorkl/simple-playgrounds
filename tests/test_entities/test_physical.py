from typing import Optional

import numpy as np

from simple_playgrounds.playground.playground import EmptyPlayground
from .mock_entities import MockPhysical


def test_traversable_traversable(custom_contour, custom_contour_2):

    playground = EmptyPlayground()

    # Two traversable shouldn't collide with either traversables or non-traversables

    ent_1 = MockPhysical(**custom_contour._asdict(), traversable=True, movable=True, mass=5)
    playground.add(ent_1, ((0, 0), 0))

    ent_2 = MockPhysical(**custom_contour_2._asdict(), traversable=True, movable=True, mass=5)
    playground.add(ent_2, ((0, 1), 0))

    playground.update()

    assert ent_1.coordinates == ((0, 0), 0)
    assert ent_2.coordinates == ((0, 1), 0)


def test_traversable_basic(custom_contour, custom_contour_2):

    playground = EmptyPlayground()

    ent_1 = MockPhysical(**custom_contour._asdict(), traversable=True, movable=True, mass=5)
    playground.add(ent_1, ((0, 0), 0))

    ent_2 = MockPhysical(**custom_contour_2._asdict(), traversable=False, movable=True, mass=5)
    playground.add(ent_2, ((0, 1), 0))

    playground.update()

    assert ent_1.coordinates == ((0, 0), 0)
    assert ent_2.coordinates == ((0, 1), 0)


def test_basic_basic(custom_contour, custom_contour_2):

    playground = EmptyPlayground()

    ent_1 = MockPhysical(**custom_contour._asdict(), traversable=False, movable=True, mass=5)
    playground.add(ent_1, ((0, 0), 0))

    ent_2 = MockPhysical(**custom_contour_2._asdict(), traversable=False, movable=False)
    playground.add(ent_2, ((0, 1), 0))

    playground.update()

    assert ent_1.coordinates != ((0, 0), 0)
    assert ent_2.coordinates == ((0, 1), 0)


def test_transparent(custom_contour):
    playground = EmptyPlayground()
    view_empty = playground.view((0, 0), (50, 50))

    ent_1 = MockPhysical(**custom_contour._asdict(), transparent=True, movable=True, mass=5)
    playground.add(ent_1, ((10, 10), 0))
    view_transparent = playground.view((0, 0), (50, 50))
    assert np.all(view_transparent == view_empty)

    view_transparent_visible = playground.view((0, 0), (50, 50), draw_invisible=True)
    assert not np.all(view_transparent == view_transparent_visible)
