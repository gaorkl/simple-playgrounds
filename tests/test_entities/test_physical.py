import pytest
import math
from simple_playgrounds.playground.playground import EmptyPlayground
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

    playground = EmptyPlayground()

    ent_1 = MockPhysicalMovable(playground, coord_center)

    assert ent_1 in playground._entities
    assert ent_1 not in playground._agents

    ent_1.remove()

    assert ent_1 in playground._entities
    assert ent_1.removed
    assert ent_1 not in playground.entities

    playground.reset()
    assert ent_1 in playground.entities


def test_size_entities_radius(radius):

    playground = EmptyPlayground()
    ent_1 = MockPhysicalFromShape(
        playground, coord_center, geometry="circle", size=radius, color=(0, 0, 1)
    )

    assert ent_1.radius == pytest.approx(radius, 1)
    assert ent_1.height == ent_1.width == pytest.approx(math.sqrt(2) * radius, 1)


def test_traversable_traversable():

    playground = EmptyPlayground()

    # Two traversable shouldn't collide with either traversables or non-traversables

    ent_1 = MockPhysicalMovable(playground, coord_center, traversable=True)
    ent_2 = MockPhysicalMovable(playground, coord_shift, traversable=True)

    playground.step()

    assert ent_1.coordinates == coord_center
    assert ent_2.coordinates == coord_shift


def test_traversable_basic():

    playground = EmptyPlayground()

    # Traversable shouldn't collide with non-traversables

    ent_1 = MockPhysicalMovable(playground, coord_center)
    ent_2 = MockPhysicalMovable(playground, coord_shift, traversable=True)

    playground.step()

    assert ent_1.coordinates == coord_center
    assert ent_2.coordinates == coord_shift


def test_basic_basic():

    playground = EmptyPlayground()

    ent_1 = MockPhysicalMovable(playground, coord_center)
    ent_2 = MockPhysicalUnmovable(playground, coord_shift)

    playground.step()

    assert ent_1.coordinates != coord_center
    assert ent_2.coordinates == coord_shift


def test_transparent_basic():

    playground = EmptyPlayground()

    ent_1 = MockPhysicalMovable(playground, coord_center, transparent=True)
    ent_2 = MockPhysicalUnmovable(playground, coord_shift)

    playground.step()

    assert ent_1.coordinates != coord_center
    assert ent_2.coordinates == coord_shift


def test_transparent_transparent():

    playground = EmptyPlayground()

    ent_1 = MockPhysicalMovable(playground, coord_center, transparent=True)
    ent_2 = MockPhysicalUnmovable(playground, coord_shift, transparent=True)

    playground.step()
    assert ent_1.coordinates != coord_center
    assert ent_2.coordinates == coord_shift


def test_non_convex_entity():

    playground = EmptyPlayground()

    ent_1 = NonConvexPlus(playground, coord_center, 40, 10)
    ent_2 = NonConvexC(playground, coord_center, 60, 20)

    for _ in range(100):
        playground.step()

    assert ent_1.coordinates == coord_center
    assert ent_2.coordinates == coord_center


def test_non_convex_entity_moving():

    playground = EmptyPlayground()

    ent_1 = NonConvexPlus(playground, coord_center, 40, 10)
    ent_2 = NonConvexC(playground, coord_shift, 40, 20)

    playground.step()

    assert ent_1.coordinates != coord_center
    assert ent_2.coordinates != coord_shift


def test_entity_from_shape(geometry):

    playground = EmptyPlayground()
    ent_1 = MockPhysicalFromShape(
        playground,
        ((10, 10), math.pi / 3),
        geometry=geometry,
        size=10,
        color=(123, 122, 54),
    )


def test_shape_approximation(shape_approx):

    playground = EmptyPlayground()

    coord = ((10, 10), math.pi / 3)
    ent_1 = NonConvexPlus_Approx(
        playground, coord, 20, 10, shape_approximation=shape_approx
    )


def test_overlapping():

    playground = EmptyPlayground()

    MockPhysicalMovable(playground, coord_center)
    MockPhysicalMovable(playground, coord_center)

    with pytest.raises(ValueError):
        MockPhysicalMovable(playground, coord_center, allow_overlapping=False)
