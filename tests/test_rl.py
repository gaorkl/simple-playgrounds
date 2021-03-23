from simple_playgrounds.agents.controllers import Random
from simple_playgrounds.agents import BaseAgent
from simple_playgrounds import Engine
from simple_playgrounds.agents.sensors import Touch
from simple_playgrounds.agents.parts import ForwardPlatform

from simple_playgrounds.playground import PlaygroundRegister

from simple_playgrounds.playgrounds.empty import SingleRoom
from simple_playgrounds.utils.position_utils import CoordinateSampler

def test_all_test_playgrounds_interactive():

    agent = BaseAgent(controller=Random(), interactive=True, platform=ForwardPlatform)

    for pg_name, pg_class in PlaygroundRegister.playgrounds['basic_rl'].items():
        playground = pg_class()

        playground.add_agent(agent, allow_overlapping=False)

        print('Starting testing of ', pg_class.__name__)

        engine = Engine(playground, time_limit=10000)
        engine.run()
        assert 0 < agent.position[0] < playground.size[0]
        assert 0 < agent.position[1] < playground.size[1]

        engine.terminate()
        playground.remove_agent(agent)
