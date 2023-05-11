import math
import random

import pytest

from spg.playground import EmptyPlayground
from spg.playground.actions import fill_action_space
from tests.mock_agents import DynamicAgentWithArm, DynamicAgentWithTrigger

center_coord = (0, 0), 0


# parametrize decorator with marks for position, angle, and rotational_range, separately
@pytest.mark.parametrize("pos", [(20, 20), (-20, -20), (10, -10)])
@pytest.mark.parametrize("angle", [-2, 1, 2, 6])
@pytest.mark.parametrize("arm_angle", [-math.pi / 4, math.pi / 3, 0])
@pytest.mark.parametrize("rotation_range", [math.pi / 4, math.pi / 3, math.pi / 2])
@pytest.mark.parametrize("arm_position", [(10, 10), (-10, -10), (10, -10)])
@pytest.mark.parametrize("Agent", [DynamicAgentWithArm, DynamicAgentWithTrigger])
def test_move(pos, angle,arm_angle, rotation_range, arm_position, Agent):

    playground = EmptyPlayground(size=(100, 100))

    agent = Agent(name="agent", arm_position=arm_position, arm_angle=arm_angle, rotation_range=rotation_range)
    playground.add(agent, (pos, angle))

    # plt_draw(playground)

    for _ in range(100):
        playground.step(playground.null_action)
        # plt_draw(playground)

    assert agent.position == pos
    assert agent.angle == angle % (2 * math.pi)

    for _ in range(100):
        playground.step(playground.action_space.sample())

    assert agent.position != pos
    assert agent.angle != angle % (2 * math.pi)

    random_pos = (random.uniform(-10, 10), random.uniform(-10, 10))
    random_angle = random.uniform(-10, 10)

    agent.move_to((random_pos, random_angle))

    assert agent.position == random_pos
    assert agent.angle == random_angle % (2 * math.pi)

    # Check that joints are correct. Agent shouldn't move
    for _ in range(100):
        playground.step(playground.null_action)

    assert agent.position == pytest.approx(random_pos, 0.001)
    assert agent.angle == pytest.approx(random_angle% (2 * math.pi), 0.001)


@pytest.mark.parametrize("arm_angle", [0, math.pi / 2, -math.pi, -math.pi / 3])
@pytest.mark.parametrize("rotation_range", [math.pi / 4, math.pi / 3, math.pi / 2])
@pytest.mark.parametrize("arm_position", [(10, 10), (-10, -10), (10, -10)])
@pytest.mark.parametrize("action", [-1, 1])
def test_move_arm(arm_position, arm_angle, rotation_range, action):
    playground = EmptyPlayground(size=(100, 100))

    agent = DynamicAgentWithArm(name="agent", arm_position=arm_position, arm_angle=arm_angle,
                                rotation_range=rotation_range)
    playground.add(agent, center_coord)

    max_angle = - action * rotation_range / 2

    arm_action = fill_action_space(playground, {
        agent.name: {
            agent.arm.name: action,
        }
    })

    for _ in range(1000):
        playground.step(arm_action)

    arm_angle_test = (agent.arm.pm_body.angle - agent.pm_body.angle - arm_angle) % (2 * math.pi)

    if arm_angle_test > math.pi:
        arm_angle_test = arm_angle_test - 2 * math.pi

    assert arm_angle_test == pytest.approx(max_angle, 0.001)

