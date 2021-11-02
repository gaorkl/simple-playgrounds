from simple_playgrounds.playgrounds.collection import *

from simple_playgrounds.engine import Engine
from simple_playgrounds.agents.controllers import Keyboard
from simple_playgrounds.agents.agents import HeadAgent

import time

my_agent = HeadAgent(controller=Keyboard(), lateral=True, interactive=True)

#################################

for playground_name, pg_class in PlaygroundRegister.playgrounds['test'].items():

    pg = pg_class()
    pg.add_agent(my_agent, allow_overlapping=False)

    engine = Engine(playground=pg, screen=True, debug=False)

    while engine.game_on:

        engine.update_screen()

        actions = {my_agent: my_agent.controller.generate_actions()}
        engine.multiple_steps(actions, 2)

        if my_agent.reward != 0:
            print(my_agent.reward)

        time.sleep(0.05)

    pg.remove_agent(my_agent)

