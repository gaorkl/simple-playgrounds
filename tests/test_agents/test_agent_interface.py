# pylint: disable=protected-access

import pytest

from spg.agent.controller import ContinuousController, RangeController
from spg.playground import Playground
from tests.mock_agents import MockAgent, MockAgentWithArm
from tests.mock_entities import MockPhysicalMovable, MockPhysicalUnmovable


def test_agent_in_playground():

    playground = Playground()
    agent = MockAgentWithArm()
    playground.add(agent)

    assert agent in playground.agents
    assert playground.elements == []
    assert agent.base in playground._shapes_to_entities.values()
    assert agent.base in agent.parts

    for part in agent.parts:
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


@pytest.fixture(scope="module", params=[1, 5])
def range_controller(request):
    return request.param


def test_range_controller(range_controller):

    controller = RangeController("range", n=range_controller)

    for n in range(range_controller):
        controller.command = n

    with pytest.raises(ValueError):
        controller.command = range_controller


@pytest.fixture(scope="module", params=[-2.12, 1.4, 0, 1.5, 2.43])
def min_controller(request):
    return request.param


@pytest.fixture(scope="module", params=[-2.42, 1.5, 0, 1.3, 2.83])
def max_controller(request):
    return request.param


def test_cont_controller(min_controller, max_controller):

    if min_controller > max_controller:
        with pytest.raises(ValueError):
            ContinuousController("continuous", min_controller, max_controller)

    else:

        controller = ContinuousController("continous", min_controller, max_controller)

        with pytest.raises(ValueError):
            controller.command = min_controller - 0.1

        with pytest.raises(ValueError):
            controller.command = max_controller + 0.1


def test_controller_forward():

    playground = Playground()
    agent = MockAgent()
    playground.add(agent)

    commands = {agent: {"forward": 1}}

    assert agent.position == (0, 0)

    for _ in range(10):
        playground.step(commands=commands)

    assert agent.position != (0, 0)
    assert agent.position.x > 0
    assert agent.position.y == 0

    # view.update()
    # view.imdisplay()

    # playground.debug_draw()


def test_controller_rotate():

    playground = Playground()
    agent = MockAgent()
    playground.add(agent)

    commands = {agent: {"angular": 1}}

    assert agent.position == (0, 0)
    assert agent.angle == 0

    playground.step(commands=commands)

    assert agent.position == (0, 0)
    assert agent.angle > 0


def test_agent_initial_position():

    playground = Playground()
    agent = MockAgent()
    playground.add(agent)

    assert agent.position == (0, 0)
    assert agent.angle == 0


def test_agent_forward_movable():

    playground = Playground()
    agent = MockAgent()
    playground.add(agent)

    obstacle = MockPhysicalMovable()
    playground.add(obstacle, ((100, 0), 0))

    commands = {agent: {"forward": agent.base.forward_controller.max}}

    for _ in range(100):
        playground.step(commands=commands)

    assert agent.position != (100, 0)
    assert agent.position.x > 100


def test_agent_overlapping():

    playground = Playground()

    unmovable = MockPhysicalUnmovable(radius=4)
    playground.add(unmovable, ((0, 0), 0))

    agent = MockAgent()

    with pytest.raises(ValueError):
        playground.add(agent, allow_overlapping=False)
