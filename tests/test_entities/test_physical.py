import numpy as np

from simple_playgrounds.playground.playground import EmptyPlayground
from tests.mock_entities import MockPhysical


def test_traversable_traversable(custom_contour, custom_contour_2):

    playground = EmptyPlayground()

    # Two traversable shouldn't collide with either traversables or non-traversables

    ent_1 = MockPhysical(contour=custom_contour, traversable=True, movable=True, mass=5)
    playground.add(ent_1, ((0, 0), 0))

    ent_2 = MockPhysical(contour=custom_contour_2, traversable=True, movable=True, mass=5)
    playground.add(ent_2, ((0, 1), 0))

    playground.update()

    assert ent_1.coordinates == ((0, 0), 0)
    assert ent_2.coordinates == ((0, 1), 0)


def test_traversable_basic(custom_contour, custom_contour_2):

    playground = EmptyPlayground()

    ent_1 = MockPhysical(contour=custom_contour, traversable=True, movable=True, mass=5)
    playground.add(ent_1, ((0, 0), 0))

    ent_2 = MockPhysical(contour=custom_contour_2, traversable=False, movable=True, mass=5)
    playground.add(ent_2, ((0, 1), 0))

    playground.update()

    assert ent_1.coordinates == ((0, 0), 0)
    assert ent_2.coordinates == ((0, 1), 0)


def test_basic_basic(custom_contour, custom_contour_2):

    playground = EmptyPlayground()

    ent_1 = MockPhysical(contour=custom_contour, traversable=False, movable=True, mass=5)
    playground.add(ent_1, ((0, 0), 0))

    ent_2 = MockPhysical(contour=custom_contour_2, traversable=False, movable=False)
    playground.add(ent_2, ((0, 1), 0))

    playground.update()

    assert ent_1.coordinates != ((0, 0), 0)
    assert ent_2.coordinates == ((0, 1), 0)


