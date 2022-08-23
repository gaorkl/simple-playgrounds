import pytest
import gc

from simple_playgrounds.playground.playground import Playground
from tests.mock_entities import (
    MockPhysicalMovable,
    MockPhysicalInteractive,
    MockHalo,
)
from simple_playgrounds.entity.physical import PhysicalEntity

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

    playground.remove(playground._entities[0], definitive=False)

    gc.collect()
    in_gc = len(
        [obj for obj in gc.get_objects() if isinstance(obj, MockPhysicalMovable)]
    )
    assert in_gc

    playground.reset()

    playground.remove(playground._entities[0], definitive=True)
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
            if isinstance(obj, MockPhysicalInteractive)
            or isinstance(obj, PhysicalEntity)
            or isinstance(obj, MockHalo)
        ]
    )
    assert in_gc

    playground.remove(playground._entities[0], definitive=False)

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

    playground.remove(playground._entities[0], definitive=True)
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
