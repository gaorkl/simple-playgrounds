import pytest
import gc

from simple_playgrounds.playground.playground import EmptyPlayground
from tests.mock_entities import (
    MockPhysicalMovable,
    MockPhysicalInteractive,
    MockHalo,
)
from simple_playgrounds.entity.physical import PhysicalEntity

coord_center = (0, 0), 0


def test_gc_del():

    playground = EmptyPlayground()

    MockPhysicalMovable(playground, coord_center)

    playground.close()
    # del playground

    gc.collect()
    for obj in gc.get_objects():
        if isinstance(obj, EmptyPlayground):
            raise ValueError
        if isinstance(obj, MockPhysicalMovable):
            raise ValueError


def test_gc_remove_physical():

    playground = EmptyPlayground()
    MockPhysicalMovable(playground, coord_center)

    gc.collect()
    in_gc = len(
        [obj for obj in gc.get_objects() if isinstance(obj, MockPhysicalMovable)]
    )
    assert in_gc

    playground._entities[0].remove(definitive=False)

    gc.collect()
    in_gc = len(
        [obj for obj in gc.get_objects() if isinstance(obj, MockPhysicalMovable)]
    )
    assert in_gc

    playground.reset()

    playground._entities[0].remove(definitive=True)
    gc.collect()
    in_gc = len(
        [obj for obj in gc.get_objects() if isinstance(obj, MockPhysicalMovable)]
    )
    assert not in_gc

    playground.close()


def test_gc_remove_anchored():

    playground = EmptyPlayground()

    MockPhysicalInteractive(
        playground, coord_center, radius=20, interaction_range=10, triggered=True
    )

    gc.collect()
    in_gc = len(
        [
            obj
            for obj in gc.get_objects()
            if isinstance(obj, MockPhysicalInteractive)
            or isinstance(obj, PhysicalEntity)
            or isinstance(obj, MockHalo)
        ]
    )
    assert in_gc

    playground._entities[0].remove(definitive=False)

    gc.collect()
    in_gc = len(
        [
            obj
            for obj in gc.get_objects()
            if isinstance(obj, MockPhysicalInteractive)
            or isinstance(obj, PhysicalEntity)
            or isinstance(obj, MockHalo)
        ]
    )
    assert in_gc

    playground.reset()

    playground._entities[0].remove(definitive=True)
    gc.collect()
    in_gc = len(
        [
            obj
            for obj in gc.get_objects()
            if isinstance(obj, MockPhysicalInteractive)
            or isinstance(obj, PhysicalEntity)
            or isinstance(obj, MockHalo)
        ]
    )
    assert not in_gc
    playground.close()
