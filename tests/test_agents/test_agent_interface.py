import math

import pytest

from spg.core.playground import EmptyPlayground
from spg.core.playground.utils import fill_action_space
from tests.mock_entities import MockDynamicElement, MockStaticElement

coord_center = (0, 0), 0


def test_agent_in_playground(any_agents_cls, playground):

    agent = any_agents_cls(
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


def test_action_spaces_dynamic(dynamic_agent_cls):

    playground = EmptyPlayground(size=(500, 200), background=(23, 23, 21))

    agent = dynamic_agent_cls(
        name="agents", arm_position=(0, 0), arm_angle=0, rotation_range=math.pi / 2
    )
    playground.add(agent, coord_center)

    for i in range(100):
        action = playground.action_space.sample()
        playground.step(action)

    assert agent.position != coord_center[0]


def test_action_spaces_static(static_agent_cls, playground):

    agent = static_agent_cls(
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


def test_null_action(any_agents_cls, playground):

    agent = any_agents_cls(
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


def test_forward(dynamic_agent_cls, playground):

    agent = dynamic_agent_cls(
        name="agents", arm_position=(0, 0), arm_angle=0, rotation_range=math.pi / 2
    )
    playground.add(agent, coord_center)

    base_action_space = agent.action_space[agent.name].shape[0]
    action_forward = tuple([1] + [0] * (base_action_space - 1))
    action = {agent.name: {agent.name: action_forward}}

    assert agent.position == (0, 0)

    action = fill_action_space(playground, action)

    for _ in range(10):
        playground.step(action)

    assert agent.position != (0, 0)
    assert agent.position.x > 0
    assert agent.position.y == 0


def test_rotate(dynamic_agent_cls, playground):

    agent = dynamic_agent_cls(
        name="agents", arm_position=(0, 0), arm_angle=0, rotation_range=math.pi / 2
    )
    playground.add(agent, coord_center)

    base_action_space = agent.action_space[agent.name].shape[0]
    action_rotate = tuple([0] * (base_action_space - 1) + [1])
    action = {agent.name: {agent.name: action_rotate}}

    assert agent.position == (0, 0)
    assert agent.angle == 0

    action = fill_action_space(playground, action)

    playground.step(action)

    assert agent.angle > 0


def test_agent_forward_movable(dynamic_agent_cls, playground):

    agent = dynamic_agent_cls(
        name="agents", arm_position=(0, 0), arm_angle=0, rotation_range=math.pi / 2
    )
    playground.add(agent, coord_center)

    base_action_space = agent.action_space[agent.name].shape[0]
    action_forward = tuple([1] + [0] * (base_action_space - 1))
    action = {agent.name: {agent.name: action_forward}}

    action = fill_action_space(playground, action)

    obstacle = MockDynamicElement()
    playground.add(obstacle, ((100, 0), 0))

    for _ in range(100):
        playground.step(action)

    assert agent.position != (100, 0)
    assert agent.position.x > 100


def test_agent_overlapping(dynamic_agent_cls, playground):

    unmovable = MockStaticElement()
    playground.add(unmovable, ((0, 0), 0))

    agent = dynamic_agent_cls(
        name="agents", arm_position=(0, 0), arm_angle=0, rotation_range=math.pi / 2
    )

    with pytest.raises(ValueError):
        playground.add(agent, coord_center, allow_overlapping=False)
