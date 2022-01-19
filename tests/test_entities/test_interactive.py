from simple_playgrounds.entity.embodied.contour import Contour
from simple_playgrounds.playground.playground import EmptyPlayground
from simple_playgrounds.common.definitions import CollisionTypes

from tests.mock_entities import MockHaloTrigger, MockHaloTriggered,\
    MockZoneTriggered, MockZoneTrigger, MockPhysical, trigger_triggers_triggered


def test_halo_halo_in_range(radius, interaction_radius):

    playground = EmptyPlayground()
    playground.add_interaction(CollisionTypes.TEST_TRIGGER, CollisionTypes.TEST_TRIGGERED, trigger_triggers_triggered)

    contour = Contour(shape='circle', radius=radius)

    ent_1 = MockPhysical(playground, ((0, 0), 0), contour=contour, movable=True, mass=5)
    halo_1 = MockHaloTrigger(ent_1, interaction_range=interaction_radius, texture=(2, 3, 4))

    ent_2 = MockPhysical(playground, ((0, 2*radius + 2*interaction_radius - 1), 0), contour=contour)
    halo_2 = MockHaloTriggered(ent_2, interaction_range=interaction_radius, texture=(2, 3, 4))

    assert not halo_1.activated and not halo_2.activated

    playground.step()

    assert halo_1.activated and halo_2.activated


def test_halo_halo_out_range(radius, interaction_radius):

    playground = EmptyPlayground()
    playground.add_interaction(CollisionTypes.TEST_TRIGGER, CollisionTypes.TEST_TRIGGERED, trigger_triggers_triggered)

    contour = Contour(shape='circle', radius=radius)

    ent_1 = MockPhysical(playground, ((0, 0), 0), contour=contour, movable=True, mass=5)
    halo_1 = MockHaloTrigger(ent_1, interaction_range=interaction_radius, texture=(2, 3, 4))

    ent_2 = MockPhysical(playground, ((0, 2*radius + 2*interaction_radius + 1), 0), contour=contour)
    halo_2 = MockHaloTriggered(anchor=ent_2, interaction_range=interaction_radius, texture=(2, 3, 4))

    assert not halo_1.activated and not halo_2.activated

    playground.step()

    assert not halo_1.activated and not halo_2.activated


def test_halo_standalone(radius, interaction_radius):

    playground = EmptyPlayground()
    playground.add_interaction(CollisionTypes.TEST_TRIGGER, CollisionTypes.TEST_TRIGGERED, trigger_triggers_triggered)


    contour = Contour(shape='circle', radius=radius)

    ent_1 = MockPhysical(playground, ((0, 0), 0), contour=contour, movable=True, mass=5)
    halo_1 = MockHaloTrigger(ent_1, interaction_range=interaction_radius, texture=(2, 3, 4))

    contour = Contour(shape='square', radius=radius)
    zone = MockZoneTriggered(playground, ((0, 2*radius + interaction_radius - 1), 0), **contour.dict_attributes)

    assert not halo_1.activated and not zone.activated

    playground.step()

    assert halo_1.activated and zone.activated
    assert halo_1.position == (0, 0)
    assert zone.position == (0, 2*radius + interaction_radius - 1)


def test_standalone_standalone():

    playground = EmptyPlayground()
    playground.add_interaction(CollisionTypes.TEST_TRIGGER, CollisionTypes.TEST_TRIGGERED, trigger_triggers_triggered)

    contour = Contour(shape='circle', radius=10)
    zone_1 = MockZoneTrigger(playground, ((0, 5), 0), **contour.dict_attributes)
    zone_2 = MockZoneTriggered(playground, ((0, -5), 0), **contour.dict_attributes)

    assert not zone_1.activated and not zone_2.activated

    playground.step()

    # static objects don't generate collisions
    assert not zone_1.activated and not zone_2.activated
