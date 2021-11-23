from simple_playgrounds.playground.playgrounds import *

from simple_playgrounds.engine import Engine
from simple_playgrounds.agent.controllers import Keyboard
from simple_playgrounds.agent.agents import HeadAgent

import time
import cv2

my_agent = HeadAgent(controller=Keyboard(), lateral=True, interactive=True)

#################################

for playground_name, pg_class in PlaygroundRegister.playgrounds['demo'].items():

    pg = pg_class()
    pg.add_agent(my_agent, allow_overlapping=False)

    engine = Engine(playground=pg, debug=False)

    while engine.game_on:

        actions = {my_agent: my_agent.controller.generate_actions()}
        engine.step(actions)

        cv2.imshow(
            'playground',
            engine.generate_playground_image()[:, :, ::-1])

        cv2.waitKey(1)

        if my_agent.reward != 0:
            print(my_agent.reward)

        time.sleep(0.05)

    pg.remove_agent(my_agent)

