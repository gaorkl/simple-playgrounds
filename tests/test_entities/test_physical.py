import math

import pytest

from spg.playground import EmptyPlayground
from tests.mock_entities import (
    DynamicElementFromGeometry,
    MockDynamicElement,
    MockStaticElement,
    NonConvexC,
    NonConvexPlus,
    NonConvexPlus_Approx,
    StaticElementFromGeometry,
)

coord_center = (0, 0), 0
coord_shift = (0, 1), 0.3


@pytest.mark.parametrize("TestElem", [MockDynamicElement, MockStaticElement])
def test_add_remove_dynamic_entity(TestElem):

    playground = EmptyPlayground(size=(10, 10))

    ent_1 = TestElem()
    playground.add(ent_1, coord_center)

    assert ent_1 in playground.elements
    assert ent_1 not in playground.agents

    playground.remove(ent_1)

    assert ent_1 not in playground.elements

    playground.reset()
    assert ent_1 not in playground.elements


@pytest.mark.parametrize(
    "TestElem", [StaticElementFromGeometry, DynamicElementFromGeometry]
)
@pytest.mark.parametrize("radius", [2, 3, 4, 5, 10, 20])
def test_size_entities_radius(radius, TestElem):

    playground = EmptyPlayground(size=(100, 100))
    ent_1 = TestElem(geometry="circle", size=radius, color=(0, 0, 1))
    playground.add(ent_1, coord_center)

    assert ent_1.radius == pytest.approx(radius, 1)
    assert ent_1.height == ent_1.width == pytest.approx(math.sqrt(2) * radius, 1)


def test_fixed_dont_move():

    playground = EmptyPlayground(size=(100, 100))

    ent_1 = MockStaticElement()
    playground.add(ent_1, coord_center)

    ent_2 = MockStaticElement()
    playground.add(ent_2, coord_shift)

    playground.step(playground.null_action)

    assert ent_1.coordinates == coord_center
    assert ent_2.coordinates == coord_shift


def test_fix_moves_movable():

    playground = EmptyPlayground(size=(100, 100))

    ent_1 = MockStaticElement()
    playground.add(ent_1, coord_center)

    ent_2 = MockDynamicElement()
    playground.add(ent_2, coord_shift)

    playground.step(playground.null_action)

    assert ent_1.coordinates == coord_center
    assert ent_2.coordinates != coord_shift


@pytest.mark.parametrize("ghost", [True, False])
def test_fix_dont_move_ghost(ghost):

    playground = EmptyPlayground(size=(100, 100))

    ent_1 = MockStaticElement()
    playground.add(ent_1, coord_center)

    ent_2 = MockDynamicElement(ghost=ghost)
    playground.add(ent_2, coord_shift)

    playground.step(playground.null_action)

    assert ent_1.coordinates == coord_center

    if ghost:
        assert ent_2.coordinates == coord_shift
    else:
        assert ent_2.coordinates != coord_shift


def test_moving_moves_movable():

    playground = EmptyPlayground(size=(100, 100))

    ent_1 = MockDynamicElement()
    playground.add(ent_1, coord_center)

    ent_2 = MockDynamicElement()
    playground.add(ent_2, coord_shift)

    playground.step(playground.null_action)

    assert ent_1.coordinates != coord_center
    assert ent_2.coordinates != coord_shift



def test_non_convex_entity():

    playground = EmptyPlayground(size=(100, 100))

    ent_1 = NonConvexPlus(40, 10, mass=1)
    playground.add(ent_1, coord_center)

    ent_2 = NonConvexC(60, 20, mass=1)

    playground.add(ent_2, coord_center)

    for _ in range(100):
        playground.step(playground.null_action)

    assert ent_1.coordinates == coord_center
    assert ent_2.coordinates == coord_center


def test_non_convex_entity_moving():

    playground = EmptyPlayground(size=(100, 100))

    ent_1 = NonConvexPlus(40, 10, mass=1)
    playground.add(ent_1, coord_center)
    ent_2 = NonConvexC(40, 20, mass=1)
    playground.add(ent_2, coord_shift)

    playground.step(playground.null_action)

    assert ent_1.coordinates != coord_center
    assert ent_2.coordinates != coord_shift


@pytest.mark.parametrize(
    "TestElem", [StaticElementFromGeometry, DynamicElementFromGeometry]
)
@pytest.mark.parametrize("geometry", ["circle", "square", "segment"])
def test_entity_from_shape(geometry, TestElem):

    playground = EmptyPlayground(size=(100, 100))
    ent_1 = TestElem(
        geometry=geometry,
        size=10,
        color=(123, 122, 54),
    )

    playground.add(ent_1, ((10, 10), math.pi / 3))


@pytest.mark.parametrize("shape_approx", ["circle", "box", "hull", "decomposition"])
def test_shape_approximation(shape_approx):

    playground = EmptyPlayground(size=(100, 100))

    coord = ((10, 10), math.pi / 3)
    ent_1 = NonConvexPlus_Approx(20, 10, shape_approximation=shape_approx, mass=1)

    playground.add(ent_1, coord)
