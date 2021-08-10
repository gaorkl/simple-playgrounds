import pytest

from simple_playgrounds.engine import Engine
from simple_playgrounds.playgrounds.layouts import SingleRoom
from simple_playgrounds.agents.agents import BaseAgent
from simple_playgrounds.agents.parts.controllers import External


def test_moving_element(basic_element):
    playground = SingleRoom(size=(200, 200))

    agent = BaseAgent(
        controller=External(),
        interactive=False,
        rotate=False,
        lateral=False
    )
    actions = {agent: {agent.longitudinal_force: 1.}}

    playground.add_agent(agent, ((50, 100), 0))
    playground.add_element(basic_element, ((100, 100), 0))

    engine = Engine(playground, time_limit=100)

    while engine.game_on:
        engine.step(actions)

    if basic_element.movable:
        assert agent.position[0] > 100
        assert basic_element.position[0] > 100
    else:
        assert basic_element.position[0] == 100