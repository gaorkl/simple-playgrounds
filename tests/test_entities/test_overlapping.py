import numpy as np
import pytest

from simple_playgrounds.playground.playground import EmptyPlayground
from .mock_entities import MockPhysical, MockZoneTrigger
from simple_playgrounds.common.contour import Contour


def test_overlap_fixed():

    playground = EmptyPlayground()

    # Two traversable shouldn't collide with either traversables or non-traversables

    contour = Contour('circle', 10, None, None)
    ent_1 = MockPhysical(**contour._asdict())
    playground.add(ent_1, ((0, 0), 0))

    ent_2 = MockPhysical(**contour._asdict())
    playground.add(ent_2, ((0, 1), 0))


def test_overlap_movable():

    playground = EmptyPlayground()

    # Two traversable shouldn't collide with either traversables or non-traversables

    contour = Contour('circle', 10, None, None)
    ent_1 = MockPhysical(**contour._asdict())
    playground.add(ent_1, ((0, 0), 0))

    ent_2 = MockPhysical(**contour._asdict())
    playground.add(ent_2, ((0, 1), 0))

    ent_3 = MockPhysical(**contour._asdict())
    with pytest.raises(ValueError):
        playground.add(ent_3, ((0, 1), 0), allow_overlapping=False)


def test_overlap_interactive():

    playground = EmptyPlayground()

    # Two traversable shouldn't collide with either traversables or non-traversables

    contour = Contour('circle', 10, None, None)
    ent_1 = MockPhysical(**contour._asdict(), traversable=True)
    playground.add(ent_1, ((0, 0), 0))

    ent_2 = MockZoneTrigger(**contour._asdict(), texture = (10, 10, 10))
    playground.add(ent_2, ((0, 1), 0), allow_overlapping=False)


