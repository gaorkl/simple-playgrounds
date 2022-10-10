import math
import random

import pytest

from spg.playground.playground import Playground
from tests.mock_agents import MockAgentWithArm


@pytest.fixture(scope="module", params=[(20, 20), (-20, -20), (10, -10)])
def pos(request):
    return request.param


@pytest.fixture(scope="module", params=[-4, 2, 1])
def angle(request):
    return request.param


@pytest.fixture(scope="module", params=[True, False])
def keep_velocity(request):
    return request.param


def test_move(pos, angle):

    playground = Playground()
    agent = MockAgentWithArm()
    playground.add(agent, (pos, angle))

    assert agent.position.x == pos[0]
    assert agent.position.y == pos[1]
    assert agent.angle == angle % (2 * math.pi)

    for _ in range(100):
        playground.step()

    assert agent.position.x == pytest.approx(pos[0], 0.001)
    assert agent.position.y == pytest.approx(pos[1], 0.001)

    random_pos = (random.uniform(-10, 10), random.uniform(-10, 10))
    random_angle = random.uniform(-10, 10)

    agent.move_to((random_pos, random_angle))

    # Check that joints are correct. Agent shouldn't move
    for _ in range(100):
        playground.step()

    assert agent.position.x == pytest.approx(random_pos[0], 0.001)
    assert agent.position.y == pytest.approx(random_pos[1], 0.001)


def test_move_reset(pos, angle):

    playground = Playground()
    agent = MockAgentWithArm()
    # agent = MockAgent()
    playground.add(agent, (pos, angle))

    commands = {agent: {"forward": 1}}

    # Check that joints are correct. Agent shouldn't move
    for _ in range(100):
        playground.step(commands=commands)

    assert agent.position.x != pytest.approx(pos[0], 0.001)
    assert agent.position.y != pytest.approx(pos[1], 0.001)

    playground.reset()

    for _ in range(100):
        playground.step()

    assert agent.position.x == pytest.approx(pos[0], 0.001)
    assert agent.position.y == pytest.approx(pos[1], 0.001)


def test_move_arm(pos, angle):

    playground = Playground()
    agent = MockAgentWithArm()
    playground.add(agent, (pos, angle))

    commands = {
        agent: {
            "left_joint": 1,
            "right_joint": -1,
        }
    }

    # Check that joints are correct. Agent shouldn't move
    for _ in range(1000):
        playground.step(commands=commands)

    # playground.debug_draw(5, size=(200, 200))

    assert math.pi / 3 + math.pi / 8 - math.pi / 20 < agent.left_arm.relative_angle
    assert agent.left_arm.relative_angle < math.pi / 3 + math.pi / 8

    assert -math.pi / 3 - math.pi / 8 < agent.right_arm.relative_angle
    assert agent.right_arm.relative_angle < -math.pi / 3 - math.pi / 8 + math.pi / 20
