from simple_playgrounds.common.contour import Contour
from simple_playgrounds.playground.playground import EmptyPlayground

# Add test Interactions to collisions
from simple_playgrounds.common.definitions import CollisionTypes
from tests.mock_entities import MockHaloTrigger, MockPhysical, MockZoneTriggered, \
    trigger_triggers_triggered, MockHaloTriggered, MockBarrier


def test_same_team(radius, interaction_radius):

    playground = EmptyPlayground()
    playground.add_interaction(CollisionTypes.TEST_TRIGGER, CollisionTypes.TEST_TRIGGERED, trigger_triggers_triggered)

    contour = Contour(shape='circle', radius=radius)

    ent_1 = MockPhysical(**contour.dict_attributes, movable=True, mass=5)
    halo = MockHaloTrigger(anchor=ent_1, interaction_range=interaction_radius, texture=(2, 3, 4))
    ent_1.add_interactive(halo)
    playground.add(ent_1, ((0, 0), 0))

    ent_1.add_to_team('team_1')

    contour = Contour(shape='square', radius=radius)
    zone = MockZoneTriggered(**contour.dict_attributes, texture=(10, 10, 10))
    zone.add_to_team('team_1')

    playground.add(zone, ((0, 2*radius + interaction_radius - 1), 0))

    playground.update()

    assert halo.activated and zone.activated


def test_different_team(radius, interaction_radius):

    playground = EmptyPlayground()
    playground.add_interaction(CollisionTypes.TEST_TRIGGER, CollisionTypes.TEST_TRIGGERED, trigger_triggers_triggered)

    contour = Contour(shape='circle', radius=radius)

    ent_1 = MockPhysical(**contour.dict_attributes, movable=True, mass=5)
    halo = MockHaloTrigger(anchor=ent_1, interaction_range=interaction_radius, texture=(2, 3, 4))
    ent_1.add_interactive(halo)
    playground.add(ent_1, ((0, 0), 0))

    ent_1.add_to_team('team_1')

    contour = Contour(shape='square', radius=radius)
    zone = MockZoneTriggered(**contour.dict_attributes, texture=(10, 10, 10))
    zone.add_to_team('team_2')

    playground.add(zone, ((0, 2*radius + interaction_radius - 1), 0))

    playground.update()

    assert not halo.activated and not zone.activated


def test_multiple_team(radius, interaction_radius):

    playground = EmptyPlayground()
    playground.add_interaction(CollisionTypes.TEST_TRIGGER, CollisionTypes.TEST_TRIGGERED, trigger_triggers_triggered)

    contour = Contour(shape='circle', radius=radius)

    ent_1 = MockPhysical(**contour.dict_attributes, movable=True, mass=5)
    halo = MockHaloTrigger(anchor=ent_1, interaction_range=interaction_radius, texture=(2, 3, 4))
    ent_1.add_interactive(halo)
    playground.add(ent_1, ((0, 0), 0))
    ent_1.add_to_team('team_1')
    ent_1.add_to_team('team_2')

    contour = Contour(shape='square', radius=radius)
    zone_1 = MockZoneTriggered(contour=contour, texture=(10, 10, 10))
    zone_1.add_to_team('team_1')
    zone_1.add_to_team('team_3')

    playground.add(zone_1, ((0, 2*radius + interaction_radius - 1), 0))

    ent_2 = MockPhysical(**contour.dict_attributes, movable=True, mass=5)
    halo_2 = MockHaloTriggered(anchor=ent_2, interaction_range=interaction_radius, texture=(2, 3, 4))
    ent_2.add_interactive(halo_2)
    playground.add(ent_2, ((0, 0), 0))
    ent_2.add_to_team('team_3')

    playground.update()

    assert halo.activated and zone_1.activated and not halo_2.activated


def test_multiple_triggered(radius, interaction_radius):

    playground = EmptyPlayground()
    playground.add_interaction(CollisionTypes.TEST_TRIGGER, CollisionTypes.TEST_TRIGGERED, trigger_triggers_triggered)

    contour = Contour(shape='circle', radius=radius)

    ent_1 = MockPhysical(**contour.dict_attributes, movable=True, mass=5)
    halo = MockHaloTrigger(anchor=ent_1, interaction_range=interaction_radius, texture=(2, 3, 4))
    ent_1.add_interactive(halo)
    playground.add(ent_1, ((0, 0), 0))
    ent_1.add_to_team('team_1')

    contour = Contour(shape='square', radius=radius)
    zone_1 = MockZoneTriggered(**contour.dict_attributes, texture=(10, 10, 10))
    zone_1.add_to_team('team_1')

    playground.add(zone_1, ((0, 0), 0))

    zone_2 = MockZoneTriggered(**contour.dict_attributes, texture=(10, 10, 10))
    zone_2.add_to_team('team_1')

    playground.add(zone_2, ((0, 0), 0))

    zone_3 = MockZoneTriggered(**contour.dict_attributes, texture=(10, 10, 10))
    zone_3.add_to_team('team_2')

    playground.add(zone_3, ((0, 0), 0))

    playground.update()

    assert halo.activated and zone_1.activated and zone_2.activated
    assert not zone_3.activated
    # assert not zone_2.activated


def test_teams_collide_same_team(custom_contour):

    playground = EmptyPlayground()
    playground.add_interaction(CollisionTypes.TEST_TRIGGER, CollisionTypes.TEST_TRIGGERED, trigger_triggers_triggered)

    ent_1 = MockPhysical(contour=custom_contour, movable=True, mass=5)
    playground.add(ent_1, ((0, 0), 0))
    ent_1.add_to_team('team_1')

    ent_2 = MockPhysical(contour=custom_contour, movable=True, mass=5)
    playground.add(ent_2, ((0, 1), 0))
    ent_2.add_to_team('team_1')

    playground.update()

    assert ent_1.position != (0, 0)
    assert ent_2.position != (0, 1)


def test_teams_collide_other_team(custom_contour):

    playground = EmptyPlayground()
    playground.add_interaction(CollisionTypes.TEST_TRIGGER, CollisionTypes.TEST_TRIGGERED, trigger_triggers_triggered)

    ent_1 = MockPhysical(contour=custom_contour, movable=True, mass=5)
    playground.add(ent_1, ((0, 0), 0))
    ent_1.add_to_team('team_1')

    ent_2 = MockPhysical(contour=custom_contour, movable=True, mass=5)
    playground.add(ent_2, ((0, 1), 0))
    ent_2.add_to_team('team_2')

    playground.update()

    assert ent_1.position != (0, 0)
    assert ent_2.position != (0, 1)


def test_teams_collide_no_team(custom_contour):

    playground = EmptyPlayground()
    playground.add_interaction(CollisionTypes.TEST_TRIGGER, CollisionTypes.TEST_TRIGGERED, trigger_triggers_triggered)

    ent_1 = MockPhysical(contour=custom_contour, movable=True, mass=5)
    playground.add(ent_1, ((0, 0), 0))
    ent_1.add_to_team('team_1')

    ent_2 = MockPhysical(contour=custom_contour, movable=True, mass=5)
    playground.add(ent_2, ((0, 1), 0))

    playground.update()

    assert ent_1.position != (0, 0)
    assert ent_2.position != (0, 1)


def test_barrier_let_team_through(custom_contour):

    playground = EmptyPlayground()

    ent_1 = MockPhysical(contour=custom_contour, movable=True, mass=5)
    playground.add(ent_1, ((0, -1), 0))
    ent_1.add_to_team('team_1')

    contour_barrier = Contour(shape='rectangle', size=(10, 10))
    barrier = MockBarrier(contour=contour_barrier, texture=(10, 10, 10), movable=False)
    barrier.add_to_team('team_1')

    playground.add(barrier, ((0, 1), 0))

    playground.update()

    assert ent_1.position == (0, -1)


def test_barrier_doesnt_block_no_team(custom_contour, custom_contour_2):

    """ Allows agent to carry flag in capture te flag scenario """

    playground = EmptyPlayground()

    ent_1 = MockPhysical(contour=custom_contour, movable=True, mass=5)
    playground.add(ent_1, ((0, -1), 0))

    barrier = MockBarrier(**custom_contour_2.dict_attributes, texture=(10, 10, 10))
    barrier.add_to_team('team_1')

    playground.add(barrier, ((0, 1), 0))

    playground.update()

    assert ent_1.position == (0, -1)


def test_barrier_without_team_blocks_team(custom_contour, custom_contour_2):

    playground = EmptyPlayground()

    ent_1 = MockPhysical(contour=custom_contour, movable=True, mass=5)
    playground.add(ent_1, ((0, -1), 0))
    ent_1.add_to_team('team_1')

    barrier = MockBarrier(contour=custom_contour_2, texture=(10, 10, 10))

    playground.add(barrier, ((0, 1), 0))

    playground.update()

    assert ent_1.position != (0, -1)


def test_barrier_block_other_teams(custom_contour, custom_contour_2):

    playground = EmptyPlayground()

    ent_1 = MockPhysical(contour=custom_contour, movable=True, mass=5)
    playground.add(ent_1, ((0, -1), 0))
    ent_1.add_to_team('team_1')

    barrier = MockBarrier(contour=custom_contour_2, texture=(10, 10, 10))
    barrier.add_to_team('team_2')

    playground.add(barrier, ((0, 1), 0))

    playground.update()

    assert ent_1.position != (0, -1)


def test_barrier_allow_multiple_teams(custom_contour):

    playground = EmptyPlayground()

    ent_1 = MockPhysical(contour=custom_contour, movable=True, mass=5)
    playground.add(ent_1, ((0, -1), 0))
    ent_1.add_to_team('team_1')

    contour_barrier = Contour(shape='rectangle', size=(10, 10))
    barrier = MockBarrier(contour=contour_barrier, texture=(10, 10, 10))
    barrier.add_to_team('team_1')
    barrier.add_to_team('team_2')

    playground.add(barrier, ((0, 1), 0))

    playground.update()

    assert ent_1.position == (0, -1)