from spg.agent import HeadAgent
from spg.element import Ball
from spg.playground import Room
from spg.utils.position import UniformCoordinateSampler
from spg.view import GUI

playground = Room(size=(500, 500))

ball = Ball()
ball.graspable = True

playground.add(ball, ((200, 0), 0))

ball = Ball()
ball.graspable = True

playground.add(ball, ((200, 40), 0))

agent = HeadAgent()
playground.add(agent)

for _ in range(50):

    angle = playground.rng.uniform(0, 8)
    sampler = UniformCoordinateSampler(
        playground, center=playground.center, size=playground.size
    )

    other_agent = HeadAgent()
    playground.add(other_agent, sampler, allow_overlapping=False)


gui = GUI(playground, agent)
gui.run()
