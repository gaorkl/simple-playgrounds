import gc

from spg.entity.physical import PhysicalEntity
from spg.playground import Playground
from tests.mock_entities import MockHalo, MockPhysicalInteractive, MockPhysicalMovable

coord_center = (0, 0), 0


def test_gc_del():

    playground = Playground()

    playground.add(MockPhysicalMovable(), coord_center)

    del playground

    gc.collect()
    for obj in gc.get_objects():
        if isinstance(obj, Playground):
            raise ValueError
        if isinstance(obj, MockPhysicalMovable):
            raise ValueError


def test_gc_remove_physical():

    playground = Playground()
    playground.add(MockPhysicalMovable(), coord_center)

    gc.collect()
    in_gc = len(
        [obj for obj in gc.get_objects() if isinstance(obj, MockPhysicalMovable)]
    )
    assert in_gc

    playground.remove(playground.elements[0], definitive=False)

    gc.collect()
    in_gc = len(
        [obj for obj in gc.get_objects() if isinstance(obj, MockPhysicalMovable)]
    )
    assert in_gc

    playground.reset()

    playground.remove(playground.elements[0], definitive=True)
    gc.collect()
    in_gc = len(
        [obj for obj in gc.get_objects() if isinstance(obj, MockPhysicalMovable)]
    )
    assert not in_gc


def test_gc_remove_anchored():

    playground = Playground()

    playground.add(
        MockPhysicalInteractive(radius=20, interaction_range=10),
        coord_center,
    )

    gc.collect()
    in_gc = len(
        [
            obj
            for obj in gc.get_objects()
            if isinstance(obj, (MockPhysicalInteractive, PhysicalEntity, MockHalo))
        ]
    )
    assert in_gc

    playground.remove(playground.elements[0], definitive=False)

    gc.collect()
    in_gc = len(
        [
            obj
            for obj in gc.get_objects()
            if isinstance(obj, (MockPhysicalInteractive, PhysicalEntity, MockHalo))
        ]
    )
    assert in_gc

    playground.reset()

    playground.remove(playground.elements[0], definitive=True)
    gc.collect()
    in_gc = len(
        [
            obj
            for obj in gc.get_objects()
            if isinstance(obj, (MockPhysicalInteractive, PhysicalEntity, MockHalo))
        ]
    )
    assert not in_gc
