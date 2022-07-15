from simple_playgrounds.playground.playgrounds.simple import WallClosedPG
from simple_playgrounds.element.basic.ball import Ball
from simple_playgrounds.agent.agents import HeadAgent

from simple_playgrounds.common.view import TopDownView


def test_scenario():

    playground = WallClosedPG(size=(1000, 200))
    ball = Ball(playground, ((200, 0), 0))
    agent = HeadAgent(playground)

    view = TopDownView(playground, zoom=1)

    view.update()
    view.imdisplay()
