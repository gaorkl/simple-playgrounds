import arcade

from spg.agent import HeadAgent
from spg.element import Ball
from spg.playground import WallClosedPG
from spg.view import GUI

playground = WallClosedPG(size=(500, 200), background=(23, 23, 21))

ball = Ball()
ball.graspable = True

playground.add(ball, ((200, 0), 0))

ball = Ball()
ball.graspable = True
playground.add(ball, ((200, 40), 0))

ball = Ball(color=(23, 184, 13))
ball.graspable = True
playground.add(ball, ((-200, 40), 0))

ball = Ball(color=arcade.color.AMETHYST)
ball.graspable = True
playground.add(ball, ((-200, 0), 0))

ball = Ball(color=arcade.color.CYAN)
ball.graspable = True
playground.add(ball, ((-200, -40), 0))


agent = HeadAgent()
playground.add(agent)

gui = GUI(playground, agent, draw_sensors=True)
gui.run()
