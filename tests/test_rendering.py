import math
from os import path as osp

import numpy as np

from simple_playgrounds.engine import Engine
from simple_playgrounds.playgrounds.collection import (PlaygroundRegister,
                                                       get_all_sensor_agent)


def test_rendering():
    agent = get_all_sensor_agent()

    pg_class = PlaygroundRegister.playgrounds['demo']['basic-deterministic']

    pg = pg_class()
    pg.add_agent(agent, ((250, 150), -3 * math.pi / 4), allow_overlapping=True)

    engine = Engine(playground=pg, screen=False, debug=False)

    engine.update_observations()
    agent_img = engine.generate_agent_image(
        agent, layout=(('sensors', 'playground'), ), with_actions=False)

    ref_location = osp.join(
        osp.dirname(osp.abspath(__file__)), 'test_rendering.npy')
    ref_img = np.load(ref_location)

    if np.linalg.norm(agent_img - ref_img) == 0.0:
        pass
    else:
        np.save('new_test_rendering', agent_img)
        raise AssertionError
