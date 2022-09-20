from spg.agent import HeadAgent
from spg.element import Ball
from spg.playground import WallClosedColorPG
from spg.view import GUI

playground = WallClosedColorPG(size=(1000, 1000))

ball = Ball()
ball.graspable = True

playground.add(ball, ((200, 0), 0))

ball = Ball()
ball.graspable = True

playground.add(ball, ((200, 40), 0))

agent = HeadAgent()
playground.add(agent)


for x in range(-200, 250, 50):
    for y in range(-50, 100, 50):

        angle = playground.rng.uniform(0, 8)

        other_agent = HeadAgent()
        playground.add(other_agent, ((x, y), angle))


gui = GUI(playground, agent)
gui.run()
