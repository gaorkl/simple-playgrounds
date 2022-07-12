import pytest

import numpy as np
from simple_playgrounds.playground.playground import EmptyPlayground
from tests.mock_agents import MockTriggerPart, MockAgentWithArm, MockHaloPart
from tests.mock_entities import (
    MockBarrier,
    MockHalo,
    MockZoneInteractive,
    active_interaction,
    passive_interaction,
)
from simple_playgrounds.common.definitions import CollisionTypes

coord_center = (0, 0), 0

# team of barrier ; team of agent ; is it blocked?
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


def test_agent_barrier(barrier_params):

    team_barrier, team_agent, barrier_blocks = barrier_params

    playground = EmptyPlayground()
    barrier = MockBarrier(playground, (30, 30), (30, -30), width=10, teams=team_barrier)

    # print(barrier_params)

    agent = MockAgentWithArm(playground, ((0, 0), 0), teams=team_agent)

    for _ in range(1000):
        playground.step()

    # assert agent.position.x < 0
    # playground.debug_draw()
    assert barrier_blocks != (agent.base.coordinates == coord_center)


def test_agent_interacts_passive():

    playground = EmptyPlayground()
    playground.add_interaction(
        CollisionTypes.PASSIVE_INTERACTOR,
        CollisionTypes.PASSIVE_INTERACTOR,
        passive_interaction,
    )

    agent = MockAgentWithArm(playground, teams="team_1")
    interactive_part_l = MockHaloPart(agent.left_arm)
    interactive_part_r = MockHaloPart(agent.right_arm)

    zone_1 = MockZoneInteractive(playground, ((30, 30), 0), 10, teams="team_1")
    zone_2 = MockZoneInteractive(playground, ((30, -30), 0), 10, teams="team_2")

    # playground.debug_draw()

    assert not interactive_part_l.activated
    assert not interactive_part_r.activated

    playground.step()

    assert zone_1.activated
    assert interactive_part_l.activated

    assert not zone_2.activated
    assert not interactive_part_r.activated


def test_agent_interacts_active():

    playground = EmptyPlayground()
    playground.add_interaction(
        CollisionTypes.ACTIVE_INTERACTOR,
        CollisionTypes.PASSIVE_INTERACTOR,
        active_interaction,
    )

    agent = MockAgentWithArm(playground, teams="team_1")
    interactive_part_l = MockTriggerPart(agent.left_arm)
    interactive_part_r = MockTriggerPart(agent.right_arm)

    zone_1 = MockZoneInteractive(playground, ((30, 30), 0), 10, teams="team_1")
    zone_2 = MockZoneInteractive(playground, ((30, -30), 0), 10, teams="team_2")

    # playground.debug_draw()

    assert not interactive_part_l.activated
    assert not interactive_part_r.activated

    playground.step()

    assert not zone_1.activated
    assert not zone_2.activated

    commands = {agent: {interactive_part_l.trigger: 1, interactive_part_r.trigger: 1}}

    playground.step(commands=commands)

    assert interactive_part_r.activated
    assert interactive_part_l.activated
    assert zone_1.activated
    assert not zone_2.activated

    playground.step()

    assert not interactive_part_r.activated
    assert not interactive_part_l.activated
    assert not zone_1.activated
    assert not zone_2.activated
