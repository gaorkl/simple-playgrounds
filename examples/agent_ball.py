from simple_playgrounds.playground.playgrounds.simple import WallClosedPG
from simple_playgrounds.element.basic.ball import Ball
from simple_playgrounds.agent.agents import HeadAgent
from simple_playgrounds.common.gui import GUI


playground = WallClosedPG(size=(500, 200))
ball = Ball(playground, ((200, 0), 0))
agent = HeadAgent(playground)

gui = GUI(playground, agent)
playground.run()
