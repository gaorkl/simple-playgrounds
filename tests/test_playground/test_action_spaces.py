import math

from spg.core.playground import EmptyPlayground
from spg.core.playground.utils import fill_action_space
from tests.mock_agents import DynamicAgent, DynamicAgentWithArm

coord_center = (0, 0), 0


def test_zero_action():
    playground = EmptyPlayground(size=(500, 200), background=(23, 23, 21))
    agent = DynamicAgent(name="agent")
    playground.add(agent, coord_center)

    playground.step(playground.null_action)

    assert agent.position == coord_center[0]
    assert agent.angle == coord_center[1]


def test_partial_action():
    playground = EmptyPlayground(size=(500, 200), background=(23, 23, 21))
    agent = DynamicAgentWithArm(
        name="agent", arm_position=(0, 0), arm_angle=0, rotation_range=math.pi / 4
    )
    playground.add(agent, coord_center)

    agent_forward_action = {agent.name: {agent.name: (1, 0, 0)}}

    action = fill_action_space(playground, agent_forward_action)

    playground.step(action)
