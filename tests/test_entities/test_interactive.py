from simple_playgrounds.playground.playground import Playground
from simple_playgrounds.common.definitions import CollisionTypes


from tests.mock_entities import (
    MockHalo,
    MockPhysicalInteractive,
    passive_interaction,
    NonConvexC,
    MockZoneInteractive,
)


coord_center = (0, 0), 0


def test_trigger():

    playground = Playground()
    playground.add_interaction(
        CollisionTypes.PASSIVE_INTERACTOR,
        CollisionTypes.PASSIVE_INTERACTOR,
        passive_interaction,
    )

    center_0 = (0, 0), 0
    trigger_1 = MockPhysicalInteractive(radius=10, interaction_range=5)
    playground.add(trigger_1, center_0)

    center_1 = (0, 25), 0
    triggered_1 = MockPhysicalInteractive(radius=10, interaction_range=5)
    playground.add(triggered_1, center_1)

    center_2 = (0, 50), 0
    triggered_2 = MockPhysicalInteractive(radius=10, interaction_range=5)
    playground.add(triggered_2, center_2)

    playground.step()

    # Assert activations are correct
    assert trigger_1.halo.activated
    assert triggered_1.halo.activated
    assert triggered_2.halo.activated

    # Assert entities don't movable
    assert trigger_1.coordinates == center_0
    assert triggered_1.coordinates == center_1
    assert triggered_2.coordinates == center_2


def test_non_convex_entity():

    playground = Playground()
    playground.add_interaction(
        CollisionTypes.PASSIVE_INTERACTOR,
        CollisionTypes.PASSIVE_INTERACTOR,
        passive_interaction,
    )

    ent_1 = NonConvexC(35, 10)
    halo_1 = MockHalo(ent_1, interaction_range=10)

    playground.add(ent_1, coord_center)

    ent_2 = MockPhysicalInteractive(radius=20, interaction_range=10)
    playground.add(ent_2, coord_center)

    playground.step()

    assert ent_1.coordinates == coord_center
    assert ent_2.coordinates == coord_center

    assert halo_1.activated
    assert ent_2.halo.activated


def test_zone_triggers():

    playground = Playground()
    playground.add_interaction(
        CollisionTypes.PASSIVE_INTERACTOR,
        CollisionTypes.PASSIVE_INTERACTOR,
        passive_interaction,
    )

    zone_1 = MockZoneInteractive(35)
    playground.add(zone_1, coord_center)

    ent_2 = MockPhysicalInteractive(radius=20, interaction_range=10)
    playground.add(ent_2, coord_center)

    playground.step()

    assert zone_1.coordinates == coord_center
    assert ent_2.coordinates == coord_center

    assert zone_1.activated
    assert ent_2.halo.activated


def test_physical_triggers():

    playground = Playground()
    playground.add_interaction(
        CollisionTypes.PASSIVE_INTERACTOR,
        CollisionTypes.PASSIVE_INTERACTOR,
        passive_interaction,
    )

    zone_1 = MockZoneInteractive(35)
    playground.add(zone_1, coord_center)

    ent_2 = MockPhysicalInteractive(radius=20, interaction_range=5)
    playground.add(ent_2, coord_center)

    playground.step()

    assert zone_1.coordinates == coord_center
    assert ent_2.coordinates == coord_center

    assert zone_1.activated
    assert ent_2.halo.activated


def test_trigger_same_team():

    playground = Playground()
    playground.add_interaction(
        CollisionTypes.PASSIVE_INTERACTOR,
        CollisionTypes.PASSIVE_INTERACTOR,
        passive_interaction,
    )

    center_0 = (0, 0), 0
    trigger_1 = MockPhysicalInteractive(radius=10, interaction_range=5, teams="team_0")
    playground.add(trigger_1, center_0)

    center_1 = (0, 25), 0
    triggered_1 = MockPhysicalInteractive(
        radius=10, interaction_range=5, teams="team_0"
    )
    playground.add(triggered_1, center_1)

    playground.step()

    # Assert activations are correct
    assert trigger_1.halo.activated
    assert triggered_1.halo.activated

    # Assert entities don't movable
    assert trigger_1.coordinates == center_0
    assert triggered_1.coordinates == center_1


def test_trigger_different_team():

    playground = Playground()
    playground.add_interaction(
        CollisionTypes.PASSIVE_INTERACTOR,
        CollisionTypes.PASSIVE_INTERACTOR,
        passive_interaction,
    )

    center_0 = (0, 0), 0
    trigger_1 = MockPhysicalInteractive(radius=10, interaction_range=5, teams="team_0")
    playground.add(trigger_1, center_0)

    center_1 = (0, 25), 0
    triggered_1 = MockPhysicalInteractive(
        radius=10, interaction_range=5, teams="team_1"
    )
    playground.add(triggered_1, center_1)

    playground.step()

    # Assert activations are correct
    assert not trigger_1.halo.activated
    assert not triggered_1.halo.activated

    # Assert entities don't movable
    assert trigger_1.coordinates == center_0
    assert triggered_1.coordinates == center_1


def test_trigger_common_team():

    playground = Playground()
    playground.add_interaction(
        CollisionTypes.PASSIVE_INTERACTOR,
        CollisionTypes.PASSIVE_INTERACTOR,
        passive_interaction,
    )

    center_0 = (0, 0), 0
    trigger_1 = MockPhysicalInteractive(
        radius=10, interaction_range=5, teams=["team_0", "team_1"]
    )
    playground.add(trigger_1, center_0)

    center_1 = (0, 25), 0
    triggered_1 = MockPhysicalInteractive(
        radius=10, interaction_range=5, teams=["team_1", "team_2"]
    )
    playground.add(triggered_1, center_1)

    playground.step()

    # Assert activations are correct
    assert trigger_1.halo.activated
    assert triggered_1.halo.activated

    # Assert entities don't movable
    assert trigger_1.coordinates == center_0
    assert triggered_1.coordinates == center_1
