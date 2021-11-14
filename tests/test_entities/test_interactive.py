

from simple_playgrounds.common.contour import Contour
from simple_playgrounds.playground.playground import EmptyPlayground

# Add test Interactions to collisions
from simple_playgrounds.common.definitions import CollisionTypes

from .mock_entities import MockHaloTrigger, MockHaloTriggered, MockZoneTriggered, MockZoneTrigger, MockPhysical, trigger_triggers_triggered


def test_halo_halo_in_range(radius, interaction_radius):

    playground = EmptyPlayground()
    playground.add_interaction(CollisionTypes.TEST_TRIGGER, CollisionTypes.TEST_TRIGGERED, trigger_triggers_triggered)

    contour = Contour('circle', radius, None, None)

    ent_1 = MockPhysical(**contour._asdict(), movable=True, mass=5)
    halo_1 = MockHaloTrigger(anchor=ent_1, interaction_range=interaction_radius, texture=(2, 3, 4))
    ent_1.add_interactive(halo_1)
    playground.add(ent_1, ((0, 0), 0))

    ent_2 = MockPhysical(**contour._asdict())
    playground.add(ent_2, ((0, 2*radius + 2*interaction_radius - 1), 0))

    halo_2 = MockHaloTriggered(anchor=ent_2, interaction_range=interaction_radius, texture=(2, 3, 4))
    ent_2.add_interactive(halo_2)

    assert not halo_1.activated and not halo_2.activated

    playground.update()

    assert halo_1.activated and halo_2.activated


def test_halo_halo_out_range(radius, interaction_radius):

    playground = EmptyPlayground()
    playground.add_interaction(CollisionTypes.TEST_TRIGGER, CollisionTypes.TEST_TRIGGERED, trigger_triggers_triggered)

    contour = Contour('circle', radius, None, None)

    ent_1 = MockPhysical(**contour._asdict(), movable=True, mass=5)
    halo_1 = MockHaloTrigger(anchor=ent_1, interaction_range=interaction_radius, texture=(2, 3, 4))
    ent_1.add_interactive(halo_1)
    playground.add(ent_1, ((0, 0), 0))

    ent_2 = MockPhysical(**contour._asdict())
    playground.add(ent_2, ((0, 2*radius + 2*interaction_radius + 1), 0))

    halo_2 = MockHaloTriggered(anchor=ent_2, interaction_range=interaction_radius, texture=(2, 3, 4))
    ent_2.add_interactive(halo_2)

    assert not halo_1.activated and not halo_2.activated

    playground.update()

    assert not halo_1.activated and not halo_2.activated


def test_halo_standalone(radius, interaction_radius):

    playground = EmptyPlayground()
    playground.add_interaction(CollisionTypes.TEST_TRIGGER, CollisionTypes.TEST_TRIGGERED, trigger_triggers_triggered)

    contour = Contour('circle', radius, None, None)

    ent_1 = MockPhysical(**contour._asdict(), movable=True, mass=5)
    halo_1 = MockHaloTrigger(anchor=ent_1, interaction_range=interaction_radius, texture=(10, 10, 10))
    ent_1.add_interactive(halo_1)

    playground.add(ent_1, ((0, 0), 0))

    contour = Contour('square', radius, None, None)
    zone = MockZoneTriggered(**contour._asdict(), texture=(10, 10, 10))

    playground.add(zone, ((0, 2*radius + interaction_radius - 1), 0))

    assert not halo_1.activated and not zone.activated

    playground.update()

    assert halo_1.activated and zone.activated
    assert halo_1.position == (0, 0)
    assert zone.position == (0, 2*radius + interaction_radius - 1)


def test_standalone_standalone():

    playground = EmptyPlayground()
    playground.add_interaction(CollisionTypes.TEST_TRIGGER, CollisionTypes.TEST_TRIGGERED, trigger_triggers_triggered)

    contour = Contour('circle', 10, None, None)
    zone_1 = MockZoneTrigger(**contour._asdict(), texture=(10, 10, 10))
    zone_2 = MockZoneTriggered(**contour._asdict(), texture=(10, 10, 10))

    playground.add(zone_1, ((0, 5), 0))
    playground.add(zone_2, ((0, -5), 0))

    assert not zone_1.activated and not zone_2.activated

    playground.update()


    # static objects don't generate collisions
    assert not zone_1.activated and not zone_2.activated




