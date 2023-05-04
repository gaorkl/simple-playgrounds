from spg import Ball
from spg import HeadAgent
from spg import Room
from spg import UniformCoordinateSampler
from spg.view import HeadAgentGUI

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


gui = HeadAgentGUI(playground, agent, random_agents=True)
gui.run()
