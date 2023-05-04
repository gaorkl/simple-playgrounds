from spg.playground import EmptyPlayground

# Add test Interactions to collisions
from tests.mock_entities import MockBarrier, MockDynamicElement

coord_center = ((0, 0), 0)
coord_shift = ((0, 1), 0)
coord_far = ((0, 1000), 0)


def test_single_barrier_not_blocking():
    playground = EmptyPlayground(size=(100, 100))

    elem = MockDynamicElement()
    playground.add(elem, coord_center)

    barrier = MockBarrier()
    playground.add(barrier, coord_shift)

    playground.step(playground.null_action)

    assert elem.position == coord_center[0]


def test_single_barrier_blocking():
    playground = EmptyPlayground(size=(100, 100))

    elem = MockDynamicElement()
    playground.add(elem, coord_center)

    barrier = MockBarrier()
    playground.add(barrier, coord_shift)

    barrier.block(elem)

    playground.step(playground.null_action)

    assert elem.position != coord_center[0]


def test_multiple_barrier_blocking():
    playground = EmptyPlayground(size=(100, 100))

    elem = MockDynamicElement()
    playground.add(elem, coord_center)

    barrier1 = MockBarrier()
    playground.add(barrier1, coord_shift)

    barrier2 = MockBarrier()
    playground.add(barrier2, coord_far)

    barrier1.block(elem)

    playground.step(playground.null_action)

    assert elem.position != coord_center[0]


def test_multiple_barrier_non_blocking():
    playground = EmptyPlayground(size=(100, 100))

    elem = MockDynamicElement()
    playground.add(elem, coord_center)

    barrier1 = MockBarrier()
    playground.add(barrier1, coord_shift)

    barrier2 = MockBarrier()
    playground.add(barrier2, coord_far)

    barrier2.block(elem)

    playground.step(playground.null_action)

    assert elem.position == coord_center[0]
