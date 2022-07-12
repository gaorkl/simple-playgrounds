import pytest
from simple_playgrounds.agent.controller import (
    ContinuousController,
    RangeController,
)

from simple_playgrounds.playground.playground import EmptyPlayground
from tests.mock_agents import MockAgent, MockAgentWithArm, MockHaloPart
from tests.mock_entities import MockPhysicalMovable, MockPhysicalUnmovable


def test_agent_in_playground():

    playground = EmptyPlayground()

    # view = TopDownView(playground,
    #                    center = (0, 0), size = (300, 300), display_uid=False)

    agent = MockAgentWithArm(playground)
    interactive_part_l = MockHaloPart(agent.left_arm)

    assert agent in playground.agents
    assert playground.entities == []
    assert agent._base in playground._shapes_to_entities.values()
    assert agent._base in agent.parts

    for part in agent.parts:
        assert part in playground._shapes_to_entities.values()
        assert part.agent == agent

    # view.update()
    # view.imdisplay()

    agent.remove(definitive=False)

    assert agent not in playground.agents
    assert not playground.space.shapes
    assert playground._shapes_to_entities != {}

    playground.reset()

    assert agent in playground.agents

    # view.update()
    # view.imdisplay()

    agent.remove(definitive=True)

    assert agent not in playground.agents
    assert not playground.space.shapes
    assert playground._shapes_to_entities == {}

    playground.reset()

    assert agent not in playground.agents


@pytest.fixture(scope="module", params=[1, 5])
def range_controller(request):
    return request.param


def test_range_controller(range_controller):

    playground = EmptyPlayground()
    agent = MockAgent(playground)
    controller = RangeController(part=agent._base, n=range_controller)

    for _ in range(200):
        assert controller.sample() in list(range(range_controller))

    controller.set_command(command=controller.sample())

    with pytest.raises(ValueError):
        controller.set_command(range_controller, hard_check=True)


@pytest.fixture(scope="module", params=[-2.12, 1.4, 0, 1.5, 2.43])
def min_controller(request):
    return request.param


@pytest.fixture(scope="module", params=[-2.42, 1.5, 0, 1.3, 2.83])
def max_controller(request):
    return request.param


def test_cont_controller(min_controller, max_controller):

    playground = EmptyPlayground()
    agent = MockAgent(playground)

    if min_controller > max_controller:
        with pytest.raises(ValueError):
            ContinuousController(min_controller, max_controller, part=agent._base)

    else:

        controller = ContinuousController(
            min_controller, max_controller, part=agent._base
        )

        with pytest.raises(ValueError):
            controller.set_command(min_controller - 0.1, hard_check=True)

        with pytest.raises(ValueError):
            controller.set_command(max_controller + 0.1, hard_check=True)


def test_controller_forward():

    playground = EmptyPlayground()
    agent = MockAgent(playground)

    # view = TopDownView(playground,
    # center = (0, 0), size = (300, 300), display_uid=False)

    commands = {agent: {agent._base.forward_controller: 1}}

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

    playground = EmptyPlayground()
    agent = MockAgent(playground)

    commands = {agent: {agent._base.angular_vel_controller: 1}}

    assert agent.position == (0, 0)
    assert agent.angle == 0

    playground.step(commands=commands)

    assert agent.position == (0, 0)
    assert agent.angle > 0


def test_agent_initial_position():

    playground = EmptyPlayground()
    agent = MockAgent(playground)

    assert agent.position == (0, 0)
    assert agent.angle == 0


def test_agent_forward_movable():

    playground = EmptyPlayground()
    agent = MockAgent(playground)

    obstacle = MockPhysicalMovable(playground, ((100, 0), 0))

    actions = {}
    for controller in agent.controllers:
        actions[controller] = controller.max

    commands = {
        agent: {agent._base.forward_controller: agent._base.forward_controller.max}
    }

    for _ in range(100):
        playground.step(commands=commands)

    assert agent.position != (100, 0)
    assert agent.position.x > 100


def test_agent_overlapping():

    playground = EmptyPlayground()

    MockPhysicalUnmovable(playground, ((0, 0), 0))

    with pytest.raises(ValueError):
        MockAgent(playground, ((0, 0), 0), allow_overlapping=False)
