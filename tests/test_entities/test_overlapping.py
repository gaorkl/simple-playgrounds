import numpy as np

from simple_playgrounds.playground.playground import EmptyPlayground
from .mock_entities import MockPhysical
from simple_playgrounds.common.contour import Contour


def test_overlap_fixed():

    playground = EmptyPlayground()

    # Two traversable shouldn't collide with either traversables or non-traversables

    contour = Contour('circle', 10, None, None)
    ent_1 = MockPhysical(**contour._asdict())
    playground.add(ent_1, ((0, 0), 0))

    ent_2 = MockPhysical(**contour._asdict())
    playground.add(ent_2, ((0, 1), 0))

    playground.update()

    assert ent_1.coordinates == ((0, 0), 0)
    assert ent_2.coordinates == ((0, 1), 0)


def test_overlap_movable():

    playground = EmptyPlayground()

    # Two traversable shouldn't collide with either traversables or non-traversables

    contour = Contour('circle', 10, None, None)
    ent_1 = MockPhysical(**contour._asdict())
    playground.add(ent_1, ((0, 0), 0))

    ent_2 = MockPhysical(**contour._asdict())
    playground.add(ent_2, ((0, 1), 0))

    playground.update()

    assert ent_1.coordinates == ((0, 0), 0)
    assert ent_2.coordinates == ((0, 1), 0)

