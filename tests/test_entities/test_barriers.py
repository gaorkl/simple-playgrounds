import pytest

from spg.playground import Playground

# Add test Interactions to collisions
from tests.mock_entities import MockBarrier, MockPhysicalMovable

coord_center = ((0, 0), 0)


@pytest.fixture(scope="module", params=[True, False])
def entity_transparent(request):
    return request.param


@pytest.fixture(scope="module", params=[True, False])
def barrier_transparent(request):
    return request.param


# team of barrier ; team of entity ; is it blocked?
@pytest.fixture(
    scope="module",
    params=[
        ("team_0", "team_0", False),
        ("team_0", None, False),
        (None, "team_0", True),
        ("team_0", "team_1", True),
        (["team_0", "team_1"], "team_0", False),
    ],
)
def barrier_params(request):
    return request.param


def test_barrier(barrier_params, entity_transparent, barrier_transparent):

    team_barrier, team_entity, barrier_blocks = barrier_params

    playground = Playground()
    barrier = MockBarrier(
        (-50, -50),
        (20, 20),
        width=10,
        teams=team_barrier,
        transparent=barrier_transparent,
    )
    playground.add(barrier, barrier.wall_coordinates)

    ent_1 = MockPhysicalMovable(teams=team_entity, transparent=entity_transparent)
    playground.add(ent_1, coord_center)

    playground.step(playground.null_action)
    assert barrier_blocks != (ent_1.coordinates == coord_center)
