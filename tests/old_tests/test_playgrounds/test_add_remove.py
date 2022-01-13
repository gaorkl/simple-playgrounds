from typing import Optional

import numpy as np

from simple_playgrounds.playground.playground import EmptyPlayground
from simple_playgrounds.common.contour import Contour
from ..mock_entities import MockPhysical


def test_add_remove_reset():

    playground = EmptyPlayground()

    contour = Contour(shape='circle', radius=10)

    # Two traversable shouldn't collide with either traversables or non-traversables

    ent_1 = MockPhysical(contour=contour, traversable=True, movable=True, mass=5, initial_coordinates=((0,0), 0)
    playground.add(ent_1, ((0, 0), 0))

    playground.remove(ent_1)

    assert not playground.space.shapes

    playground.reset()

    assert ent_1 in playground._entities


def test_add_temporary_remove_reset():

    playground = EmptyPlayground()

    contour = Contour(shape='circle', radius=10)

    # Two traversable shouldn't collide with either traversables or non-traversables

    ent_1 = MockPhysical(contour=contour, traversable=True, movable=True, mass=5, initial_coordinates=((0,0), 0, temporary=True)
    playground.add(ent_1, ((0, 0), 0))

    playground.remove(ent_1)

    assert not playground.space.shapes

    playground.reset()

    assert ent_1 not in playground._entities
