from spg.agent import HeadAgent
from spg.element import Ball
from spg.playground import WallClosedColorPG
from spg.view import GUI

playground = WallClosedColorPG(size=(500, 200))

ball = Ball()
ball.graspable = True

playground.add(ball, ((200, 0), 0))

ball = Ball()
ball.graspable = True

playground.add(ball, ((200, 40), 0))

agent = HeadAgent()
playground.add(agent)

gui = GUI(playground, agent, draw_sensors=True)
gui.run()
