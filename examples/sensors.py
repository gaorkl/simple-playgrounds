from spg.agent import HeadAgent
from spg.element import Ball
from spg.playground import Room
from spg.view import HeadAgentGUI

playground = Room(size=(500, 200), background=(23, 23, 21))

ball = Ball()
ball.graspable = True

playground.add(ball, ((200, 0), 0))

ball = Ball()
ball.graspable = True

playground.add(ball, ((200, 40), 0))

agent = HeadAgent()
playground.add(agent)

gui = HeadAgentGUI(playground, agent, draw_sensors=True)
gui.run()
