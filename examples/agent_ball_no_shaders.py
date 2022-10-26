import arcade

from spg.agent import HeadAgent
from spg.element import Ball, TiledAlternateColorWall
from spg.playground import Room
from spg.view import HeadAgentGUI

# import arcade

playground = Room(
    size=(500, 200),
    background=(23, 23, 21),
    wall_cls=TiledAlternateColorWall,
    use_shaders=False,
)

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

gui = HeadAgentGUI(playground, agent, draw_sensors=True)
gui.run()
