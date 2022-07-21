from simple_playgrounds.playground.playground import EmptyPlayground
from tests.mock_entities import (
    MockPhysicalMovable,
    MockZoneInteractive,
    MockPhysicalInteractive,
)

coord_center = (0, 0), 0


def test_playground_interface_basic_element():

    playground = EmptyPlayground()

    assert not playground._entities

    ent_1 = MockPhysicalMovable(playground, coord_center)
    assert ent_1 in playground.entities

    ent_1.remove()
    assert ent_1 not in playground.entities
    assert ent_1 in playground._entities
    assert ent_1._removed

    playground.reset()

    assert ent_1 in playground.entities
    assert not ent_1.removed

    ent_1.remove(definitive=True)

    assert ent_1 not in playground.entities
    assert ent_1 not in playground._entities
    assert ent_1._removed

    playground.reset()

    assert ent_1 not in playground.entities
    assert ent_1 not in playground._entities
    assert ent_1._removed

    assert not playground.space.shapes
    assert not playground.space.bodies

    playground.close()


def test_playground_interface_interactive_element():

    playground = EmptyPlayground()

    assert not playground._entities

    ent_1 = MockZoneInteractive(playground, coord_center, 35)

    assert ent_1 in playground.entities

    ent_1.remove()

    assert ent_1 not in playground.entities
    assert ent_1 in playground._entities
    assert ent_1._removed

    playground.reset()

    assert ent_1 in playground.entities
    assert not ent_1.removed

    ent_1.remove(definitive=True)

    assert ent_1 not in playground.entities
    assert ent_1 not in playground._entities
    assert ent_1._removed

    playground.reset()

    assert ent_1 not in playground.entities
    assert ent_1 not in playground._entities
    assert ent_1._removed

    assert not playground.space.shapes
    assert not playground.space.bodies

    playground.close()


def test_playground_interface_anchored_interactive_element():

    playground = EmptyPlayground()

    assert not playground._entities

    ent_1 = MockPhysicalInteractive(
        playground, coord_center, radius=20, interaction_range=10, triggered=True
    )

    assert ent_1 in playground.entities

    ent_1.remove()

    assert ent_1 not in playground.entities
    assert ent_1 in playground._entities
    assert ent_1._removed

    playground.reset()

    assert ent_1 in playground.entities
    assert not ent_1.removed

    ent_1.remove(definitive=True)

    assert ent_1 not in playground.entities
    assert ent_1 not in playground._entities
    assert ent_1._removed

    playground.reset()

    assert ent_1 not in playground.entities
    assert ent_1 not in playground._entities
    assert ent_1._removed

    assert not playground.space.shapes
    assert not playground.space.bodies

    playground.close()
