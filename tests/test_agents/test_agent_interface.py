# pylint: disable=protected-access

import pytest

from spg import Playground
from spg.playground.actions import fill_action_space
from tests.mock_agents import MockAgent, MockAgentWithArm, MockAgentWithTriggerArm
from tests.mock_entities import MockPhysicalMovable, MockPhysicalUnmovable


def test_agent_in_playground():

    playground = Playground()
    agent = MockAgentWithArm(name="agent")
    playground.add(agent)

    assert agent in playground.agents
    assert playground.elements == []
    assert agent.base in playground._shapes_to_entities.values()
    assert agent.base in agent.parts.values()

    for part in agent.parts.values():
        assert part in playground._shapes_to_entities.values()
        assert part.agent == agent

    playground.remove(agent, definitive=False)

    assert agent not in playground.agents
    assert not playground.space.shapes
    assert playground._shapes_to_entities

    playground.reset()

    assert agent in playground.agents

    playground.remove(agent, definitive=True)

    assert agent not in playground.agents
    assert not playground.space.shapes
    assert not playground._shapes_to_entities

    playground.reset()

    assert agent not in playground.agents


def test_action_spaces():

    playground = Playground(size=(200, 200))
    agent = MockAgentWithTriggerArm(name="agent")
    playground.add(agent)

    for i in range(100):
        action = playground.action_space.sample()
        playground.step(action)

    assert agent.position != (0, 0)


def test_null_action():

    playground = Playground(size=(200, 200))
    agent = MockAgentWithTriggerArm(name="agent")
    playground.add(agent)

    for i in range(100):
        action = playground.action_space.sample()
        playground.step(action)

    for i in range(1000):
        playground.step(playground.null_action)

    assert pytest.approx(agent.base.velocity) == (0, 0)


def test_forward():

    playground = Playground()
    agent = MockAgent(name="agent")
    playground.add(agent)

    action = {agent.name: {"base": {"motor": {"forward_force": 0.9}}}}

    assert agent.position == (0, 0)

    action = fill_action_space(playground, action)

    for _ in range(10):
        playground.step(action)

    assert agent.position != (0, 0)
    assert agent.position.x > 0
    assert agent.position.y == 0

    # view.update()
    # view.imdisplay()

    # playground.debug_draw()


def test_rotate():

    playground = Playground()
    agent = MockAgent(name="agent")
    playground.add(agent)

    action = {agent.name: {"base": {"motor": {"angular_velocity": 0.9}}}}

    assert agent.position == (0, 0)
    assert agent.angle == 0

    playground.step(action)

    assert agent.position == (0, 0)
    assert agent.angle > 0


def test_agent_initial_position():

    playground = Playground()
    agent = MockAgent(name="agent")
    playground.add(agent)

    assert agent.position == (0, 0)
    assert agent.angle == 0


def test_agent_forward_movable():

    playground = Playground()
    agent = MockAgent(name="agent")
    playground.add(agent)

    obstacle = MockPhysicalMovable()
    playground.add(obstacle, ((100, 0), 0))

    action = {agent.name: {"base": {"motor": {"forward_force": 0.9}}}}

    for _ in range(100):
        playground.step(action)

    assert agent.position != (100, 0)
    assert agent.position.x > 100


def test_agent_overlapping():

    playground = Playground()

    unmovable = MockPhysicalUnmovable(radius=4)
    playground.add(unmovable, ((0, 0), 0))

    agent = MockAgent(name="agent")

    with pytest.raises(ValueError):
        playground.add(agent, allow_overlapping=False)
