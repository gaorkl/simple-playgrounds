from spg.playground import WallClosedPG
from spg.element import Ball
from spg.agent import HeadAgent


def test_scenario():

    playground = WallClosedPG(size=(1000, 200))
    ball = Ball()
    playground.add(ball, ((200, 0), 0))

    agent = HeadAgent()
    playground.add(agent)

    commands = {agent: {agent.base.forward_controller: 1}}

    for _ in range(200):
        playground.step(commands=commands)

    assert ball.position != (200, 0)
    assert agent.position != (0, 0)
