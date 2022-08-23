import random
import numpy as np

from simple_playgrounds.common.view import TopDownView
from simple_playgrounds.playground.playgrounds.simple import WallClosedPG
from simple_playgrounds.element.ball import Ball
from simple_playgrounds.agent.agents import HeadAgent


def test_move_object():

    playground = WallClosedPG(size=(300, 200))
    ball = Ball()
    playground.add(ball, ((100, 20), 0))

    agent = HeadAgent()
    playground.add(agent)

    view = TopDownView(playground)

    view.update()
    img_init = view.get_np_img()

    random.seed(2)

    for _ in range(50):
        commands = {
            agent: {
                agent.base.forward_controller: random.uniform(0, 1),
                agent.base.angular_vel_controller: random.uniform(-1, 1),
            }
        }

        playground.step(commands=commands)

    assert ball.position != (200, 0)
    assert agent.position != (0, 0)

    view.update()
    img_after_mvt = view.get_np_img()

    assert not np.all(img_after_mvt == img_init)

    playground.reset()
    view.update()
    img_after_reset = view.get_np_img()

    assert np.all(img_init == img_after_reset)


def test_delete_object():

    playground = WallClosedPG(size=(300, 200))
    ball = Ball()
    playground.add(ball, ((100, 0), 0))

    agent = HeadAgent()
    playground.add(agent)

    view = TopDownView(playground)

    view.update()
    img_init = view.get_np_img()

    playground.remove(ball)

    view.update()
    img_after_mvt = view.get_np_img()

    assert not np.all(img_after_mvt == img_init)

    playground.reset()
    view.update()

    img_after_reset = view.get_np_img()

    assert np.all(img_init == img_after_reset)


def test_delete_agent():

    playground = WallClosedPG(size=(300, 200))
    ball = Ball()
    playground.add(ball, ((100, 0), 0))
    agent = HeadAgent()
    playground.add(agent)

    view = TopDownView(playground)

    view.update()
    img_init = view.get_np_img()

    playground.remove(agent)

    view.update()
    img_after_mvt = view.get_np_img()

    assert not np.all(img_after_mvt == img_init)

    playground.reset()
    view.update()

    img_after_reset = view.get_np_img()

    assert np.all(img_init == img_after_reset)
