import pytest

from spg.playground import Playground
from tests.mock_agents import (
    MockAgent,
    MockAgentWithTriggerArm,
    MockTriggerPart,
    MockAgentWithArm,
    MockHaloPart,
)
from tests.mock_entities import (
    MockBarrier,
    MockPhysicalMovable,
    MockZoneInteractive,
    active_interaction,
    passive_interaction,
)
from spg.utils.definitions import CollisionTypes

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

    playground = Playground()

    agent = MockAgentWithArm(teams=team_agent)
    playground.add(agent, coord_center)

    for _ in range(1000):
        playground.step()

    barrier = MockBarrier((10, 30), (10, -30), width=10, teams=team_barrier)
    playground.add(barrier, barrier.wall_coordinates)

    for _ in range(1000):
        playground.step()

    moved = agent.position != (0, 0)

    assert barrier_blocks == moved


def test_agent_interacts_passive():

    playground = Playground()
    playground.add_interaction(
        CollisionTypes.PASSIVE_INTERACTOR,
        CollisionTypes.PASSIVE_INTERACTOR,
        passive_interaction,
    )

    agent = MockAgentWithArm(teams="team_1")
    interactive_part_l = MockHaloPart(agent.left_arm)
    agent.left_arm.add(interactive_part_l)

    interactive_part_r = MockHaloPart(agent.right_arm)
    agent.right_arm.add(interactive_part_r)
    playground.add(agent)

    zone_1 = MockZoneInteractive(10, teams="team_1")
    playground.add(zone_1, ((30, 30), 0))

    zone_2 = MockZoneInteractive(10, teams="team_2")
    playground.add(zone_2, ((30, -30), 0))

    assert not interactive_part_l.activated
    assert not interactive_part_r.activated

    playground.step()

    assert zone_1.activated
    assert interactive_part_l.activated

    assert not zone_2.activated
    assert not interactive_part_r.activated


def test_agent_interacts_active():

    playground = Playground()
    playground.add_interaction(
        CollisionTypes.ACTIVE_INTERACTOR,
        CollisionTypes.PASSIVE_INTERACTOR,
        active_interaction,
    )

    agent = MockAgentWithTriggerArm(teams="team_1")
    playground.add(agent)

    zone_1 = MockZoneInteractive(10, teams="team_1")
    playground.add(zone_1, ((30, 30), 0))

    zone_2 = MockZoneInteractive(10, teams="team_2")
    playground.add(zone_2, ((30, -30), 0))

    assert not agent.left_arm.interactor.activated
    assert not agent.right_arm.interactor.activated
    assert not zone_1.activated
    assert not zone_2.activated

    playground.step()

    assert not agent.left_arm.interactor.activated
    assert not agent.right_arm.interactor.activated
    assert not zone_1.activated
    assert not zone_2.activated

    print(zone_1.teams, zone_1.pm_shapes[0].filter)
    print(zone_2.teams, zone_2.pm_shapes[0].filter)

    print(agent.left_arm.interactor._teams)
    print(agent.right_arm.interactor._teams)
    commands = {agent: {agent.left_arm.trigger: 1, agent.right_arm.trigger: 1}}

    playground.step(commands=commands)

    assert agent.left_arm.interactor.activated
    assert agent.right_arm.interactor.activated
    assert zone_1.activated
    assert not zone_2.activated

    playground.step()

    assert not agent.left_arm.interactor.activated
    assert not agent.right_arm.interactor.activated
    assert not zone_1.activated
    assert not zone_2.activated


def test_agent_grasping():

    playground = Playground()

    agent = MockAgentWithArm()
    agent.left_arm.add_grasper()
    playground.add(agent)

    elem = MockPhysicalMovable()
    elem.graspable = True
    playground.add(elem, ((60, 60), 0))

    commands = {agent: {agent.left_arm.grasper_controller: 1}}

    playground.step(commands=commands)

    assert elem in agent.left_arm.grasper._grasped_entities
    assert len(agent.left_arm.grasper._grasped_entities) == 1
