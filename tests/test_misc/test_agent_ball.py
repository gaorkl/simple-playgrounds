from spg.agent import HeadAgent
from spg.element import Ball
from spg.playground import Room


def test_scenario():

    playground = Room(size=(1000, 200))
    ball = Ball()
    playground.add(ball, ((200, 0), 0))

    agent = HeadAgent()
    playground.add(agent)

    commands = {agent: {"forward": 1}}

    for _ in range(200):
        playground.step(commands=commands)

    assert ball.position != (200, 0)
    assert agent.position != (0, 0)
