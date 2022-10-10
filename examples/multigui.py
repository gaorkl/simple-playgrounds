# pylint: disable=import-outside-toplevel

from multiprocessing import Pool

from spg.agent import HeadAgent
from spg.element import Ball
from spg.playground import Room
from spg.view import HeadAgentGUI


def run_environment(env_id):

    import arcade

    playground = Room(size=(500, 200), background=(23, 23, 21))
    playground.window.set_caption(str(env_id))

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

    gui = HeadAgentGUI(playground, agent, draw_sensors=False)
    gui.run()


if __name__ == "__main__":

    with Pool(10) as p:
        p.map(run_environment, range(10))
