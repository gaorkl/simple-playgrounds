from spg.playground import Playground
from tests.mock_entities import (
    MockPhysicalMovable,
    MockZoneInteractive,
    MockPhysicalInteractive,
)

coord_center = (0, 0), 0


def test_playground_interface_basic_element():

    playground = Playground()

    assert not playground._elements

    ent_1 = MockPhysicalMovable()
    playground.add(ent_1, coord_center)
    assert ent_1 in playground.elements

    playground.remove(ent_1)
    assert ent_1 not in playground.elements
    assert ent_1 in playground._elements
    assert ent_1._removed

    playground.reset()

    assert ent_1 in playground.elements
    assert not ent_1.removed

    playground.remove(ent_1, definitive=True)

    assert ent_1 not in playground.elements
    assert ent_1 not in playground._elements
    assert ent_1._removed

    playground.reset()

    assert ent_1 not in playground.elements
    assert ent_1 not in playground._elements
    assert ent_1._removed

    assert not playground.space.shapes
    assert not playground.space.bodies


def test_playground_interface_interactive_element():

    playground = Playground()

    assert not playground._elements

    ent_1 = MockZoneInteractive(35)
    playground.add(ent_1, coord_center)

    assert ent_1 in playground.elements

    playground.remove(ent_1)

    assert ent_1 not in playground.elements
    assert ent_1 in playground._elements
    assert ent_1._removed

    playground.reset()

    assert ent_1 in playground.elements
    assert not ent_1.removed

    playground.remove(ent_1, definitive=True)

    assert ent_1 not in playground.elements
    assert ent_1 not in playground._elements
    assert ent_1._removed

    playground.reset()

    assert ent_1 not in playground.elements
    assert ent_1 not in playground._elements
    assert ent_1._removed

    assert not playground.space.shapes
    assert not playground.space.bodies


def test_playground_interface_anchored_interactive_element():

    playground = Playground()

    assert not playground._elements

    ent_1 = MockPhysicalInteractive(radius=20, interaction_range=10)
    playground.add(ent_1, coord_center)

    assert ent_1 in playground.elements

    playground.remove(ent_1)

    assert ent_1 not in playground.elements
    assert ent_1 in playground._elements
    assert ent_1._removed

    playground.reset()

    assert ent_1 in playground.elements
    assert not ent_1.removed

    playground.remove(ent_1, definitive=True)

    assert ent_1 not in playground.elements
    assert ent_1 not in playground._elements
    assert ent_1._removed

    playground.reset()

    assert ent_1 not in playground.elements
    assert ent_1 not in playground._elements
    assert ent_1._removed

    assert not playground.space.shapes
    assert not playground.space.bodies
