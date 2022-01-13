from simple_playgrounds.entity.embodied.contour import Contour
from simple_playgrounds.playground.playground import EmptyPlayground

# Add test Interactions to collisions
from simple_playgrounds.common.definitions import CollisionTypes
from tests.mock_entities import MockHaloTrigger, MockPhysical, MockZoneTriggered, \
    trigger_triggers_triggered, MockHaloTriggered, MockBarrier


coord_0 = ((0, 0), 0)


def test_same_team(radius, interaction_radius):

    playground = EmptyPlayground()
    playground.add_interaction(CollisionTypes.TEST_TRIGGER, CollisionTypes.TEST_TRIGGERED, trigger_triggers_triggered)

    contour = Contour(shape='circle', radius=radius)

    ent_1 = MockPhysical(playground, coord_0, **contour.dict_attributes, movable=True, mass=5, teams='team_1')
    halo = MockHaloTrigger(ent_1, interaction_range=interaction_radius)

    contour = Contour(shape='square', radius=radius)
    zone = MockZoneTriggered(playground, ((0, 2*radius + interaction_radius - 1), 0), **contour.dict_attributes, teams=['team_1'])

    playground.step()

    assert halo.activated and zone.activated


def test_different_team(radius, interaction_radius):

    playground = EmptyPlayground()
    playground.add_interaction(CollisionTypes.TEST_TRIGGER, CollisionTypes.TEST_TRIGGERED, trigger_triggers_triggered)

    contour = Contour(shape='circle', radius=radius)

    ent_1 = MockPhysical(playground, coord_0, **contour.dict_attributes, movable=True, mass=5, teams='team_1')
    halo = MockHaloTrigger(ent_1, interaction_range=interaction_radius)

    contour = Contour(shape='square', radius=radius)
    zone = MockZoneTriggered(playground, ((0, 2*radius + interaction_radius - 1), 0), **contour.dict_attributes, teams='team_2')

    playground.step()

    assert not halo.activated and not zone.activated


def test_multiple_team(radius, interaction_radius):

    playground = EmptyPlayground()
    playground.add_interaction(CollisionTypes.TEST_TRIGGER, CollisionTypes.TEST_TRIGGERED, trigger_triggers_triggered)

    contour = Contour(shape='circle', radius=radius)

    ent_1 = MockPhysical(playground, coord_0, **contour.dict_attributes, movable=True, mass=5, teams=['team_1', 'team_2'])
    halo = MockHaloTrigger(anchor=ent_1, interaction_range=interaction_radius)

    contour = Contour(shape='square', radius=radius)
    zone_1 = MockZoneTriggered(playground, coord_0, contour=contour, teams=['team_1', 'team_3'])

    ent_2 = MockPhysical(playground, coord_0, **contour.dict_attributes, movable=True, mass=5, teams='team_3')
    halo_2 = MockHaloTriggered(ent_2, interaction_range=interaction_radius)

    playground.step()

    assert halo.activated and zone_1.activated and not halo_2.activated


def test_multiple_triggered(radius, interaction_radius):

    playground = EmptyPlayground()
    playground.add_interaction(CollisionTypes.TEST_TRIGGER, CollisionTypes.TEST_TRIGGERED, trigger_triggers_triggered)

    contour = Contour(shape='circle', radius=radius)

    ent_1 = MockPhysical(playground, coord_0, **contour.dict_attributes, movable=True, mass=5, teams = 'team_1')
    halo = MockHaloTrigger(anchor=ent_1, interaction_range=interaction_radius)

    contour = Contour(shape='square', radius=radius)
    zone_1 = MockZoneTriggered(playground, coord_0, **contour.dict_attributes, teams='team_1')

    zone_2 = MockZoneTriggered(playground, coord_0, **contour.dict_attributes, teams='team_1')

    zone_3 = MockZoneTriggered(playground, coord_0, **contour.dict_attributes, teams='team_2')

    playground.step()

    assert halo.activated and zone_1.activated and zone_2.activated
    assert not zone_3.activated
    # assert not zone_2.activated


def test_teams_collide_same_team(custom_contour):

    playground = EmptyPlayground()
    playground.add_interaction(CollisionTypes.TEST_TRIGGER, CollisionTypes.TEST_TRIGGERED, trigger_triggers_triggered)

    ent_1 = MockPhysical(playground, coord_0, **custom_contour.dict_attributes, movable=True, mass=5, teams='team_1')

    ent_2 = MockPhysical(playground, ((0, 1), 0), **custom_contour.dict_attributes, movable=True, mass=5, teams='team_1')

    playground.step()

    assert ent_1.position != (0, 0)
    assert ent_2.position != (0, 1)


def test_teams_collide_other_team(custom_contour):

    playground = EmptyPlayground()
    playground.add_interaction(CollisionTypes.TEST_TRIGGER, CollisionTypes.TEST_TRIGGERED, trigger_triggers_triggered)

    ent_1 = MockPhysical(playground, coord_0, **custom_contour.dict_attributes, movable=True, mass=5, teams='team_1')

    ent_2 = MockPhysical(playground, ((0, 1), 0), **custom_contour.dict_attributes, movable=True, mass=5, teams='team_2')

    playground.step()

    assert ent_1.position != (0, 0)
    assert ent_2.position != (0, 1)


def test_teams_collide_no_team(custom_contour):

    playground = EmptyPlayground()
    playground.add_interaction(CollisionTypes.TEST_TRIGGER, CollisionTypes.TEST_TRIGGERED, trigger_triggers_triggered)

    ent_1 = MockPhysical(playground, coord_0, **custom_contour.dict_attributes, movable=True, mass=5, teams = 'team_1')

    ent_2 = MockPhysical(playground, ((0, 1), 0), **custom_contour.dict_attributes, movable=True, mass=5)

    playground.step()

    assert ent_1.position != (0, 0)
    assert ent_2.position != (0, 1)


def test_barrier_let_team_through(custom_contour):

    playground = EmptyPlayground()

    ent_1 = MockPhysical(playground, ((0, -1), 0), **custom_contour.dict_attributes, movable=True, mass=5, teams='team_1')

    contour_barrier = Contour(shape='rectangle', size=(10, 10))
    barrier = MockBarrier(playground, ((0, 1), 0), contour=contour_barrier, movable=False, teams='team_1')

    playground.step()

    assert ent_1.position == (0, -1)


def test_barrier_doesnt_block_no_team(custom_contour, custom_contour_2):

    """ Allows agent to carry flag in capture te flag scenario """

    playground = EmptyPlayground()

    ent_1 = MockPhysical(playground, ((0, -1), 0), **custom_contour.dict_attributes, movable=True, mass=5)

    barrier = MockBarrier(playground, ((0, 1), 0), **custom_contour_2.dict_attributes, teams='team_1')

    playground.step()

    assert ent_1.position == (0, -1)


def test_barrier_without_team_blocks_team(custom_contour, custom_contour_2):

    playground = EmptyPlayground()

    ent_1 = MockPhysical(playground, ((0, -1), 0), **custom_contour.dict_attributes, movable=True, mass=5, teams='team_1')

    MockBarrier(playground, ((0, 1), 0), **custom_contour_2.dict_attributes)

    playground.step()

    assert ent_1.position != (0, -1)


def test_barrier_block_other_teams(custom_contour, custom_contour_2):

    playground = EmptyPlayground()

    ent_1 = MockPhysical(playground, ((0, -1), 0), **custom_contour.dict_attributes, movable=True, mass=5, teams='team_1')

    barrier = MockBarrier(playground, ((0, 1), 0), contour=custom_contour_2, teams='team_2')

    playground.step()

    assert ent_1.position != (0, -1)


def test_barrier_allow_multiple_teams(custom_contour):

    playground = EmptyPlayground()

    ent_1 = MockPhysical(playground, ((0, -1), 0), **custom_contour.dict_attributes, movable=True, mass=5, teams='team_1')

    contour_barrier = Contour(shape='rectangle', size=(10, 10))
    barrier = MockBarrier(playground, ((0, 1), 0), contour=contour_barrier, teams=['team_1', 'team_2'])

    playground.step()

    assert ent_1.position == (0, -1)
