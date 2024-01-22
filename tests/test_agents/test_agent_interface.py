import math

import pytest

from spg.core.playground import Playground
from spg.core.playground.utils import fill_action_space
from tests.mock_agents import (
    DynamicAgent,
    DynamicAgentWithArm,
    DynamicAgentWithTrigger,
    StaticAgent,
    StaticAgentWithArm,
    StaticAgentWithTrigger,
)
from tests.mock_entities import MockDynamicElement, MockStaticElement

coord_center = (0, 0), 0


@pytest.mark.parametrize(
    "Agent",
    [
        StaticAgent,
        StaticAgentWithArm,
        StaticAgentWithTrigger,
        DynamicAgent,
        DynamicAgentWithArm,
        DynamicAgentWithTrigger,
    ],
)
def test_agent_in_playground(Agent):

    playground = Playground(size=(200, 200))
    agent = Agent(
        name="agents", arm_position=(0, 0), arm_angle=0, rotation_range=math.pi / 2
    )
    playground.add(agent, coord_center)

    assert agent in playground.agents
    assert playground.elements == []
    assert agent in playground.shapes_to_entities.values()

    for part in agent.attached:
        assert part in playground.shapes_to_entities.values()
        assert part.base == agent

    playground.remove(agent)

    assert agent not in playground.agents
    assert not playground.space.shapes

    playground.reset()
    assert not playground.space.shapes
    assert not playground.shapes_to_entities


@pytest.mark.parametrize(
    "Agent", [DynamicAgent, DynamicAgentWithArm, DynamicAgentWithTrigger]
)
def test_action_spaces_dynamic(Agent):

    playground = Playground(size=(200, 200))
    agent = Agent(
        name="agents", arm_position=(0, 0), arm_angle=0, rotation_range=math.pi / 2
    )
    playground.add(agent, coord_center)

    for i in range(100):
        action = playground.action_space.sample()
        playground.step(action)

    assert agent.position != coord_center[0]


@pytest.mark.parametrize(
    "Agent", [StaticAgent, StaticAgentWithArm, StaticAgentWithTrigger]
)
def test_action_spaces_static(Agent):

    playground = Playground(size=(200, 200))
    agent = Agent(
        name="agents", arm_position=(0, 0), arm_angle=0, rotation_range=math.pi / 2
    )
    playground.add(agent, coord_center)

    if hasattr(agent, "arm"):
        arm_pos = agent.arm.position

    for i in range(100):
        action = playground.action_space.sample()
        playground.step(action)

    assert agent.position == coord_center[0]

    if hasattr(agent, "arm"):
        assert agent.arm.position != arm_pos


@pytest.mark.parametrize(
    "Agent", [DynamicAgent, DynamicAgentWithArm, DynamicAgentWithTrigger]
)
def test_null_action(Agent):

    playground = Playground(size=(200, 200))
    agent = Agent(
        name="agents", arm_position=(0, 0), arm_angle=0, rotation_range=math.pi / 2
    )
    playground.add(agent, coord_center)

    for i in range(1000):
        playground.step(playground.null_action)

    assert agent.base.velocity == (0, 0)
    assert agent.base.angular_velocity == 0
    assert agent.coordinates == coord_center

    for i in range(100):
        action = playground.action_space.sample()
        playground.step(action)

    for i in range(1000):
        playground.step(playground.null_action)

    assert pytest.approx(agent.base.velocity) == (0, 0)


@pytest.mark.parametrize(
    "Agent", [DynamicAgent, DynamicAgentWithArm, DynamicAgentWithTrigger]
)
def test_forward(Agent):

    playground = Playground(size=(200, 200))
    agent = Agent(
        name="agents", arm_position=(0, 0), arm_angle=0, rotation_range=math.pi / 2
    )
    playground.add(agent, coord_center)

    action = {agent.name: {agent.name: (1, 0, 0)}}

    assert agent.position == (0, 0)

    action = fill_action_space(playground, action)

    for _ in range(10):
        playground.step(action)

    assert agent.position != (0, 0)
    assert agent.position.x > 0
    assert agent.position.y == 0


@pytest.mark.parametrize(
    "Agent", [DynamicAgent, DynamicAgentWithArm, DynamicAgentWithTrigger]
)
def test_rotate(Agent):

    playground = Playground(size=(200, 200))
    agent = Agent(
        name="agents", arm_position=(0, 0), arm_angle=0, rotation_range=math.pi / 2
    )
    playground.add(agent, coord_center)

    action = {agent.name: {agent.name: (0, 0, 1)}}

    assert agent.position == (0, 0)
    assert agent.angle == 0

    action = fill_action_space(playground, action)

    playground.step(action)

    assert agent.angle > 0


@pytest.mark.parametrize(
    "Agent", [DynamicAgent, DynamicAgentWithArm, DynamicAgentWithTrigger]
)
def test_agent_forward_movable(Agent):

    playground = Playground(size=(200, 200))
    agent = Agent(
        name="agents", arm_position=(0, 0), arm_angle=0, rotation_range=math.pi / 2
    )
    playground.add(agent, coord_center)

    action = {agent.name: {agent.name: (1, 0, 0)}}

    action = fill_action_space(playground, action)

    obstacle = MockDynamicElement()
    playground.add(obstacle, ((100, 0), 0))

    for _ in range(100):
        playground.step(action)

    assert agent.position != (100, 0)
    assert agent.position.x > 100


@pytest.mark.parametrize(
    "Agent", [DynamicAgent, DynamicAgentWithArm, DynamicAgentWithTrigger]
)
def test_agent_overlapping(Agent):

    playground = Playground(size=(200, 200))

    unmovable = MockStaticElement()
    playground.add(unmovable, ((0, 0), 0))

    agent = Agent(
        name="agents", arm_position=(0, 0), arm_angle=0, rotation_range=math.pi / 2
    )

    with pytest.raises(ValueError):
        playground.add(agent, coord_center, allow_overlapping=False)
