import pytest

from simple_playgrounds.entity.embodied.contour import Contour
from simple_playgrounds.playground.playground import EmptyPlayground

# Add test Interactions to collisions
from simple_playgrounds.common.definitions import CollisionTypes
from tests.mock_entities import MockPhysicalMovable, MockBarrier


coord_center = ((0, 0), 0)

@pytest.fixture(scope="module", params=[True, False])
def entity_transparent(request):
    return request.param

@pytest.fixture(scope="module", params=[True, False])
def barrier_transparent(request):
    return request.param


# team of barrier ; team of entity ; is it blocked?
@pytest.fixture(scope="module", params=[
    ('team_0', 'team_0', False),
    ('team_0', None, False),
    (None, 'team_0', True),
    ('team_0', 'team_1', True),
    (['team_0', 'team_1'], 'team_0', False),
])
def barrier_params(request):
    return request.param


def test_barrier(barrier_params, entity_transparent, barrier_transparent):

    team_barrier, team_entity, barrier_blocks = barrier_params

    playground = EmptyPlayground()
    barrier = MockBarrier(playground, (-50, -50), (20, 20), width = 10, teams=team_barrier, transparent = barrier_transparent)

    ent_1 = MockPhysicalMovable(playground, coord_center, teams=team_entity, transparent=entity_transparent)

    playground.step()
    assert barrier_blocks != (ent_1.coordinates == coord_center)


