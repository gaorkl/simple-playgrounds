import pytest

from spg.playground import Playground

# Add test Interactions to collisions
from spg.utils.definitions import CollisionTypes
from tests.mock_entities import (
    MockPhysicalInteractive,
    MockZoneInteractive,
    passive_interaction,
)

coord_0 = ((0, 0), 0)

# teams of element 1 ; team of element 2 ; is interacting?


@pytest.fixture(
    scope="module",
    params=[
        ("team_0", "team_0", True),
        ("team_0", "team_1", False),
        (None, "team_0", True),
        (None, None, True),
        ("team_0", None, True),
        (["team_0", "team_1"], "team_0", True),
        ("team_0", ["team_0", "team_1"], True),
        ("team_0", ["team_2", "team_1"], False),
    ],
)
def team_params(request):
    return request.param


coord_1 = ((0, 0), 0)
coord_2 = ((0, 1), 0)


def test_team_phys_phys(team_params):

    playground = Playground()
    playground.add_interaction(
        CollisionTypes.PASSIVE_INTERACTOR,
        CollisionTypes.PASSIVE_INTERACTOR,
        passive_interaction,
    )

    team_1, team_2, interacts = team_params

    ent_1 = MockPhysicalInteractive(teams=team_1, interaction_range=10)
    playground.add(ent_1, coord_1)

    ent_2 = MockPhysicalInteractive(teams=team_2, interaction_range=10)
    playground.add(ent_2, coord_2)

    playground.step()

    triggered = ent_1.halo.activated and ent_2.halo.activated

    assert triggered == interacts
    assert ent_1.coordinates != coord_1 and ent_2.coordinates != coord_2


def test_team_phys_halo(team_params):

    playground = Playground()
    playground.add_interaction(
        CollisionTypes.PASSIVE_INTERACTOR,
        CollisionTypes.PASSIVE_INTERACTOR,
        passive_interaction,
    )

    team_1, team_2, interacts = team_params

    ent_1 = MockPhysicalInteractive(teams=team_1, interaction_range=10)
    playground.add(ent_1, coord_1)

    zone_1 = MockZoneInteractive(35, teams=team_2)
    playground.add(zone_1, coord_2)

    playground.step()

    assert (ent_1.halo.activated and zone_1.activated) or (
        (not ent_1.halo.activated) and (not zone_1.activated)
    )
    triggered = ent_1.halo.activated and zone_1.activated

    assert triggered == interacts
    assert ent_1.coordinates == coord_1 and zone_1.coordinates == coord_2
