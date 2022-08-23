import pytest
import math
from simple_playgrounds.playground.playground import Playground
from tests.mock_entities import (
    MockPhysicalMovable,
    MockPhysicalUnmovable,
    NonConvexPlus,
    NonConvexC,
    MockPhysicalFromShape,
    NonConvexPlus_Approx,
)

coord_center = (0, 0), 0
coord_shift = (0, 1), 0.3


def test_add_remove_entities():

    playground = Playground()

    ent_1 = MockPhysicalMovable()
    playground.add(ent_1, coord_center)

    assert ent_1 in playground._entities
    assert ent_1 not in playground._agents

    playground.remove(ent_1)

    assert ent_1 in playground._entities
    assert ent_1.removed
    assert ent_1 not in playground.entities

    playground.reset()
    assert ent_1 in playground.entities


def test_size_entities_radius(radius):

    playground = Playground()
    ent_1 = MockPhysicalFromShape(geometry="circle", size=radius, color=(0, 0, 1))
    playground.add(ent_1, coord_center)

    assert ent_1.radius == pytest.approx(radius, 1)
    assert ent_1.length == ent_1.width == pytest.approx(math.sqrt(2) * radius, 1)


def test_traversable_traversable():

    playground = Playground()

    # Two traversable shouldn't collide with either traversables or non-traversables

    ent_1 = MockPhysicalMovable(traversable=True)
    playground.add(ent_1, coord_center)

    ent_2 = MockPhysicalMovable(traversable=True)
    playground.add(ent_2, coord_shift)

    playground.step()

    assert ent_1.coordinates == coord_center
    assert ent_2.coordinates == coord_shift


def test_traversable_basic():

    playground = Playground()

    # Traversable shouldn't collide with non-traversables

    ent_1 = MockPhysicalMovable()
    playground.add(ent_1, coord_center)

    ent_2 = MockPhysicalMovable(traversable=True)
    playground.add(ent_2, coord_shift)

    playground.step()

    assert ent_1.coordinates == coord_center
    assert ent_2.coordinates == coord_shift


def test_basic_basic():

    playground = Playground()

    ent_1 = MockPhysicalMovable()
    playground.add(ent_1, coord_center)

    ent_2 = MockPhysicalUnmovable()
    playground.add(ent_2, coord_shift)

    playground.step()

    assert ent_1.coordinates != coord_center
    assert ent_2.coordinates == coord_shift


def test_transparent_basic():

    playground = Playground()

    ent_1 = MockPhysicalMovable(transparent=True)
    playground.add(ent_1, coord_center)

    ent_2 = MockPhysicalUnmovable()
    playground.add(ent_2, coord_shift)

    playground.step()

    assert ent_1.coordinates != coord_center
    assert ent_2.coordinates == coord_shift


def test_transparent_transparent():

    playground = Playground()

    ent_1 = MockPhysicalMovable(transparent=True)
    playground.add(ent_1, coord_center)

    ent_2 = MockPhysicalUnmovable(transparent=True)
    playground.add(ent_2, coord_shift)

    playground.step()
    assert ent_1.coordinates != coord_center
    assert ent_2.coordinates == coord_shift


def test_non_convex_entity():

    playground = Playground()

    ent_1 = NonConvexPlus(40, 10)
    playground.add(ent_1, coord_center)

    ent_2 = NonConvexC(60, 20)
    playground.add(ent_2, coord_center)

    for _ in range(100):
        playground.step()

    assert ent_1.coordinates == coord_center
    assert ent_2.coordinates == coord_center


def test_non_convex_entity_moving():

    playground = Playground()

    ent_1 = NonConvexPlus(40, 10)
    playground.add(ent_1, coord_center)
    ent_2 = NonConvexC(40, 20)
    playground.add(ent_2, coord_shift)

    playground.step()

    assert ent_1.coordinates != coord_center
    assert ent_2.coordinates != coord_shift


def test_entity_from_shape(geometry):

    playground = Playground()
    ent_1 = MockPhysicalFromShape(
        geometry=geometry,
        size=10,
        color=(123, 122, 54),
    )

    playground.add(ent_1, ((10, 10), math.pi / 3))


def test_shape_approximation(shape_approx):

    playground = Playground()

    coord = ((10, 10), math.pi / 3)
    ent_1 = NonConvexPlus_Approx(20, 10, shape_approximation=shape_approx)

    playground.add(ent_1, coord)


def test_overlapping():

    playground = Playground()

    playground.add(MockPhysicalMovable(), coord_center)
    playground.add(MockPhysicalMovable(), coord_center)

    with pytest.raises(ValueError):
        playground.add(MockPhysicalMovable(), coord_center, allow_overlapping=False)
