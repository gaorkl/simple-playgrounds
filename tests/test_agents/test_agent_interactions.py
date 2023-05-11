# pylint: disable=protected-access
import math

import numpy as np
import pytest

from spg.playground import EmptyPlayground
from tests.mock_agents import DynamicAgentWithTrigger, DynamicAgentWithArm, DynamicAgent, StaticAgentWithTrigger, \
    DynamicAgentWithGrasper, MockGraspable
from tests.mock_entities import MockBarrier
from tests.mock_interactives import ActivableZone

coord_center = (0, 0), 0

from spg.playground.actions import fill_action_space


@pytest.mark.parametrize("Agent", [DynamicAgent, DynamicAgentWithArm, DynamicAgentWithTrigger])
def test_agent_barrier(Agent):
    playground = EmptyPlayground(size=(100, 100))

    agent = Agent(name="agent", arm_position=(0, 0), arm_angle=0)

    barrier = MockBarrier()
    playground.add(barrier, coord_center)

    barrier.block(agent)

    for _ in range(1000):
        playground.step(playground.null_action)

    assert agent.position != coord_center


@pytest.mark.parametrize("Agent", [StaticAgentWithTrigger, DynamicAgentWithTrigger])
def test_agent_interacts_activable(Agent):
    playground = EmptyPlayground(size=(100, 100))

    agent = Agent(name="agent", arm_position=(0, 0), arm_angle=0)
    playground.add(agent, coord_center)

    zone = ActivableZone(radius=100)
    playground.add(zone, coord_center)

    assert not agent.trigger.activated

    playground.step(playground.null_action)

    assert zone.activated
    assert agent.trigger.activated


def test_agent_grasping():
    playground = EmptyPlayground(size=(100, 100))

    agent = DynamicAgentWithGrasper(name="agent", arm_position=(10, 10), arm_angle=math.pi / 4, grasper_radius=20)
    playground.add(agent, coord_center)

    elem = MockGraspable()
    playground.add(elem, ((50, 50), 0))

    action = {agent.name: {agent.grasper.name: 1}}
    action = fill_action_space(playground, action)

    playground.step(action)

    assert elem in agent.grasper.grasped
    assert len(agent.grasper.grasped) == 1

    playground.step(playground.null_action)

    assert elem not in agent.grasper.grasped
    assert len(agent.grasper.grasped) == 0
    assert len(elem.grasped_by) == 0


def test_agent_grasping_multiple():
    playground = EmptyPlayground(size=(100, 100))

    agent = DynamicAgentWithGrasper(name="agent", arm_position=(10, 10), arm_angle=math.pi / 4, grasper_radius=20,
                                    rotation_range=math.pi / 2)
    playground.add(agent, coord_center)

    elem1 = MockGraspable()
    playground.add(elem1, ((50, 50), 0))

    elem3 = MockGraspable()
    playground.add(elem3, ((50, 50), 0))

    elem2 = MockGraspable()
    playground.add(elem2, ((-50, 50), 0))

    action = {agent.name: {agent.grasper.name: 1}}
    action = fill_action_space(playground, action)

    playground.step(action)

    assert elem1 in agent.grasper.grasped
    assert elem3 in agent.grasper.grasped
    assert elem2 not in agent.grasper.grasped
    assert len(agent.grasper.grasped) == 2

    playground.step(playground.null_action)

    assert elem1 not in agent.grasper.grasped
    assert elem2 not in agent.grasper.grasped
    assert len(agent.grasper.grasped) == 0
    assert len(elem1.grasped_by) == 0
    assert len(elem2.grasped_by) == 0


def test_grasp_then_move():

    playground = EmptyPlayground(size=(100, 100))

    agent = DynamicAgentWithGrasper(name="agent", arm_position=(10, 10), arm_angle=math.pi / 4, grasper_radius=20,
                                    rotation_range=math.pi / 2)

    playground.add(agent, coord_center)

    elem1 = MockGraspable()
    playground.add(elem1, ((50, 50), 0))

    # calculate distance between agent and elem1
    distance = math.sqrt((agent.position[0] - elem1.position[0]) ** 2 + (agent.position[1] - elem1.position[1]) ** 2)

    for _ in range(100):
        base_action = np.random.rand(3) * 2 - 1
        action = {agent.name: {agent.grasper.name: 1, agent.name: base_action}}
        action = fill_action_space(playground, action)
        playground.step(action)

    assert elem1 in agent.grasper.grasped
    assert len(agent.grasper.grasped) == 1

    new_distance = math.sqrt(
        (agent.position[0] - elem1.position[0]) ** 2 + (agent.position[1] - elem1.position[1]) ** 2)

    assert new_distance == pytest.approx(distance, rel = 0.1)
    assert agent.position != coord_center[0]
    assert elem1.position != (50, 50)
