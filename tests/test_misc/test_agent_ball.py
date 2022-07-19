from simple_playgrounds.playground.playgrounds.simple import WallClosedPG
from simple_playgrounds.element.basic.ball import Ball
from simple_playgrounds.agent.agents import HeadAgent

def test_scenario():

    playground = WallClosedPG(size=(1000, 200))
    ball = Ball(playground, ((200, 0), 0))
    agent = HeadAgent(playground)

    commands = {agent: {agent.base.forward_controller: 10}}

    for _ in range(200):
        playground.step(commands=commands)

    assert ball.position != (200, 0)
    assert agent.position != (0, 0)
