from simple_playgrounds.agent.part.interactives import Grasper
from simple_playgrounds.entity.interactive import Graspable
from simple_playgrounds.playground.playgrounds.simple import WallClosedPG
from simple_playgrounds.element.ball import Ball
from simple_playgrounds.agent.agents import HeadAgent
from simple_playgrounds.common.gui import GUI


playground = WallClosedPG(size=(500, 200))
ball = Ball(playground, ((200, 0), 0))
Graspable(ball)
ball = Ball(playground, ((200, 40), 0))
Graspable(ball)


agent = HeadAgent(playground)

grasp = Grasper(agent.base)

gui = GUI(playground, agent)
playground.run()
