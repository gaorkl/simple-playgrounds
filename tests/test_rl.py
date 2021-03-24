from simple_playgrounds.agents.controllers import Random
from simple_playgrounds.agents import BaseAgent
from simple_playgrounds import Engine
from simple_playgrounds.agents.parts import ForwardPlatform

from simple_playgrounds.playground import PlaygroundRegister


def test_all_test_playgrounds_interactive():

    agent = BaseAgent(controller=Random(), interactive=True, platform=ForwardPlatform)

    for _, pg_class in PlaygroundRegister.playgrounds['basic_rl'].items():
        playground = pg_class()

        playground.add_agent(agent, allow_overlapping=False)

        print('Starting testing of ', pg_class.__name__)

        engine = Engine(playground, time_limit=1000)
        engine.run()
        assert 0 < agent.position[0] < playground.size[0]
        assert 0 < agent.position[1] < playground.size[1]

        engine.terminate()
        playground.remove_agent(agent)
