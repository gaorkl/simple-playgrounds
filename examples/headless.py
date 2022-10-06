# pylint: disable=import-outside-toplevel

import time
from multiprocessing import Pool


def run_environment(headless):

    if headless:
        import pyglet

        pyglet.options["headless"] = True

    import random

    import arcade

    from spg.agent import HeadAgent
    from spg.element import Ball
    from spg.playground import Room

    playground = Room(size=(500, 200), background=(23, 23, 21))

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

    for _ in range(10000):

        agent_command = {
            agent: {
                agent.base.forward_controller: random.uniform(0, 1),
                agent.base.angular_vel_controller: random.uniform(-1, 1),
            }
        }

        playground.step(commands=agent_command)

    return True


if __name__ == "__main__":

    hl = [True, False, True, False, True, True, False, False, True, True]

    t = time.time()
    with Pool(4) as p:
        time_completion = p.map(run_environment, hl)

    print(f"Computing {len(hl)} environments of 10000 ts in {sum(time_completion)} sec")
