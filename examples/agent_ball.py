from simple_playgrounds.agent.part.interactives import Grasper
from simple_playgrounds.playground.playgrounds.simple import WallClosedPG
from simple_playgrounds.element.ball import Ball
from simple_playgrounds.agent.agents import HeadAgent
from simple_playgrounds.common.gui import GUI


playground = WallClosedPG(size=(500, 200))

ball = Ball()
ball.graspable = True

playground.add(ball, ((200, 0), 0))

ball = Ball()
ball.graspable = True

playground.add(ball, ((200, 40), 0))

agent = HeadAgent()
grasper = Grasper(agent.base)
playground.add(agent)

gui = GUI(playground, agent)
gui.run()
