from spg.agent.interactor import Grasper
from spg.playground import WallClosedPG
from spg.element import Ball
from spg.agent import HeadAgent
from spg.view import GUI


playground = WallClosedPG(size=(500, 200))

ball = Ball()
ball.graspable = True

playground.add(ball, ((200, 0), 0))

ball = Ball()
ball.graspable = True

playground.add(ball, ((200, 40), 0))

agent = HeadAgent()
playground.add(agent)

gui = GUI(playground, agent)
gui.run()

playground.debug_draw()
