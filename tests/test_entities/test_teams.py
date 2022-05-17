import pytest

from simple_playgrounds.playground.playground import EmptyPlayground

# Add test Interactions to collisions
from simple_playgrounds.common.definitions import CollisionTypes
from tests.mock_entities import MockPhysicalInteractive, trigger_triggers_triggered, MockZoneInteractive

coord_0 = ((0, 0), 0)

# teams of element 1 ; team of element 2 ; is interacting?
@pytest.fixture(scope="module", params=[
    ('team_0', 'team_0', True),
    ('team_0', 'team_1', False),
    (None, 'team_0', False),
    (None, None, True),
    ('team_0', None, True),
    (['team_0', 'team_1'], 'team_0', True),
    ('team_0', ['team_0', 'team_1'], True),
    ('team_0', ['team_2', 'team_1'], False),
])

def team_params(request):
    return request.param

coord_1 = ((0, 0), 0)
coord_2 = ((0, 1), 0)

def test_team_phys_phys(team_params):

    playground = EmptyPlayground()
    playground.add_interaction(CollisionTypes.TEST_TRIGGER, CollisionTypes.TEST_TRIGGERED, trigger_triggers_triggered)

    team_1, team_2, interacts = team_params

    ent_1 = MockPhysicalInteractive(playground, coord_1, teams=team_1, interaction_range=10, trigger=True)

    ent_2 = MockPhysicalInteractive(playground, coord_2, teams=team_2, interaction_range=10, triggered=True)

    playground.step()

    triggered = ent_1.halo.activated and ent_2.halo.activated

    assert triggered == interacts
    assert ent_1.coordinates != coord_1 and ent_2.coordinates != coord_2


def test_team_phys_halo(team_params):

    playground = EmptyPlayground()
    playground.add_interaction(CollisionTypes.TEST_TRIGGER, CollisionTypes.TEST_TRIGGERED, trigger_triggers_triggered)

    team_1, team_2, interacts = team_params

    ent_1 = MockPhysicalInteractive(playground, coord_1, teams=team_1, interaction_range=10, trigger=True)

    zone_1 = MockZoneInteractive(playground, coord_2, 35, teams=team_2, triggered=True)

    playground.step()

    assert (ent_1.halo.activated and zone_1.activated) or ( (not ent_1.halo.activated) and (not zone_1.activated))
    triggered = ent_1.halo.activated and zone_1.activated

    assert triggered == interacts
    assert ent_1.coordinates == coord_1 and zone_1.coordinates == coord_2
