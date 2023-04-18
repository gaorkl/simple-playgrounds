import pytest

from spg.playground import Playground
from spg.utils.actions import fill_action_space, zero_action_space
from tests.mock_agents import MockAgent


def test_zero_action():

    playground = Playground()
    agent = MockAgent(name="agent")
    playground.add(agent)

    action = zero_action_space(playground)

    playground.step(action)


def test_partial_action():

    playground = Playground()
    agent = MockAgent(name="agent")
    playground.add(agent)

    agent_forward_action = {agent.name: {
        "base": { "motor": { "forward_force": 1}}}}

    action = fill_action_space(playground, agent_forward_action)

    playground.step(action)


