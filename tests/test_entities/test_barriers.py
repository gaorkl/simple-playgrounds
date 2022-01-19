from simple_playgrounds.entity.embodied.contour import Contour
from simple_playgrounds.playground.playground import EmptyPlayground

# Add test Interactions to collisions
from simple_playgrounds.common.definitions import CollisionTypes
from tests.mock_entities import MockHaloTrigger, MockPhysical, MockZoneTriggered, \
    trigger_triggers_triggered, MockHaloTriggered, MockBarrier


coord_0 = ((0, 0), 0)


def test_barrier_lets_team_through(custom_contour):

    playground = EmptyPlayground()

    ent_1 = MockPhysical(playground, ((0, -1), 0), **custom_contour.dict_attributes, movable=True, mass=5, teams='team_1')

    contour_barrier = Contour(shape='rectangle', size=(10, 10))
    barrier = MockBarrier(playground, ((0, 1), 0), contour=contour_barrier, movable=False, teams='team_1')

    playground.step()

    assert ent_1.position == (0, -1)


# test_barrier_traversable
# test barrier transparent

def test_barrier_allows_no_team(custom_contour, custom_contour_2):

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


def test_barrier_blocks_other_teams(custom_contour, custom_contour_2):

    playground = EmptyPlayground()

    ent_1 = MockPhysical(playground, ((0, -1), 0), **custom_contour.dict_attributes, movable=True, mass=5, teams='team_1')

    barrier = MockBarrier(playground, ((0, 1), 0), contour=custom_contour_2, teams='team_2')

    playground.step()

    assert ent_1.position != (0, -1)


def test_barrier_allow_multiple_teams(custom_contour):

    playground = EmptyPlayground()

    ent_1 = MockPhysical(playground, ((0, -1), 0), **custom_contour.dict_attributes, movable=True, mass=5, teams=['team_1', 'team_2'])

    contour_barrier = Contour(shape='rectangle', size=(10, 10))
    barrier = MockBarrier(playground, ((0, 1), 0), contour=contour_barrier, teams=['team_1', 'team_2'])

    playground.step()

    assert ent_1.position == (0, -1)
