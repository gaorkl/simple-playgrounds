# pylint: disable=protected-access

import pytest

from spg.agent.device.interactor import GraspHold
from spg.playground import Playground
from spg.utils.definitions import CollisionTypes
from tests.mock_agents import MockAgentWithArm, MockAgentWithTriggerArm, Detector
from tests.mock_entities import (
    MockBarrier,
    MockPhysicalMovable,
    MockZoneInteractive,
    active_interaction,
    passive_interaction,
)

coord_center = (0, 0), 0

from spg.utils.actions import fill_action_space

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

    agent = MockAgentWithArm(name='agent', teams=team_agent)
    playground.add(agent, coord_center)

    for _ in range(1000):
        playground.step(playground.null_action)

    barrier = MockBarrier((10, 30), (10, -30), width=10, teams=team_barrier)
    playground.add(barrier, barrier.wall_coordinates)

    for _ in range(1000):
        playground.step(playground.null_action)

    moved = agent.position != (0, 0)

    assert barrier_blocks == moved


def test_agent_interacts_passive():

    playground = Playground()
    playground.add_interaction(
        CollisionTypes.PASSIVE_INTERACTOR,
        CollisionTypes.PASSIVE_INTERACTOR,
        passive_interaction,
    )

    agent = MockAgentWithArm(name='agent', teams="team_1")
    interactive_part_l = Detector(agent.left_arm, name='part_l')
    agent.left_arm.add(interactive_part_l)

    interactive_part_r = Detector(agent.right_arm, name='part_r')
    agent.right_arm.add(interactive_part_r)
    playground.add(agent)

    zone_1 = MockZoneInteractive(10, teams="team_1")
    playground.add(zone_1, ((30, 30), 0))

    zone_2 = MockZoneInteractive(10, teams="team_2")
    playground.add(zone_2, ((30, -30), 0))

    assert not interactive_part_l.activated
    assert not interactive_part_r.activated

    playground.step(playground.null_action)

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

    agent = MockAgentWithTriggerArm(name="agent", teams="team_1")
    playground.add(agent)

    zone_1 = MockZoneInteractive(10, teams="team_1")
    playground.add(zone_1, ((30, 30), 0))

    zone_2 = MockZoneInteractive(10, teams="team_2")
    playground.add(zone_2, ((30, -30), 0))

    assert not agent.left_arm.trigger.triggered
    assert not agent.right_arm.trigger.triggered
    assert not zone_1.activated
    assert not zone_2.activated

    playground.step(playground.null_action)

    assert not agent.left_arm.trigger.triggered
    assert not agent.right_arm.trigger.triggered
    assert not zone_1.activated
    assert not zone_2.activated

    action = {agent.name: {"left_arm": { 'trigger':1}, 
                           "right_arm": {'trigger':1}}
                           
              }

    action = fill_action_space(playground, action)

    playground.step(action=action)

    assert agent.left_arm.trigger.triggered
    assert agent.right_arm.trigger.triggered
    assert zone_1.activated
    assert not zone_2.activated

    playground.step(playground.null_action)

    assert not agent.left_arm.trigger.triggered
    assert not agent.right_arm.trigger.triggered
    assert not zone_1.activated
    assert not zone_2.activated


def test_agent_grasping():

    playground = Playground()

    agent = MockAgentWithArm(name="agent")
    grasper = GraspHold(agent.left_arm, name='grasper')
    agent.left_arm.add(grasper)
    playground.add(agent)

    elem = MockPhysicalMovable()
    elem.graspable = True
    playground.add(elem, ((60, 60), 0))

    action = {
        agent.name: {
            "left_arm": {
                 "grasper": 1
                }
            }
        }

    action = fill_action_space(playground, action)

    playground.step(action)

    assert elem in agent.left_arm.grasper._grasped_entities
    assert len(agent.left_arm.grasper._grasped_entities) == 1
