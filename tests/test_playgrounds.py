from simple_playgrounds.engine import Engine

from simple_playgrounds.agent.agents import BaseAgent
from simple_playgrounds.device.sensors import Touch
from simple_playgrounds.agent.controllers import RandomContinuous

from simple_playgrounds.playground.layouts import SingleRoom
from simple_playgrounds.common.position_utils import CoordinateSampler


# Add/remove agent from a playground
def test_add_remove_agent(base_forward_agent_random):
    playground_1 = SingleRoom(size=(200, 200))
    playground_2 = SingleRoom(size=(200, 200))
    agent = base_forward_agent_random
    playground_1.add_agent(agent)
    playground_1.remove_agent(agent)
    assert playground_1.agents == []
    playground_2.add_agent(agent)


def test_add_remove_agent_in_area(base_forward_agent_random):
    playground_1 = SingleRoom((800, 400))
    agent = base_forward_agent_random

    areas = {
        'up': [0, 800, 0, 200],
        'down': [0, 800, 200, 400],
        'right': [400, 800, 0, 400],
        'left': [0, 400, 0, 400],
        'up-right': [400, 800, 0, 200],
        'up-left': [0, 400, 0, 200],
        'down-right': [400, 800, 200, 400],
        'down-left': [0, 400, 200, 400],
        'center': [200, 600, 100, 300]
    }

    for area_name, coord in areas.items():

        location, size = playground_1.grid_rooms[0][0].get_partial_area(
            area_name)

        pos_area_sampler = CoordinateSampler(location,
                                             area_shape='rectangle',
                                             size=size)

        playground_1.add_agent(agent, pos_area_sampler)

        min_x, max_x, min_y, max_y = coord

        assert min_x < agent.position[0] < max_x
        assert min_y < agent.position[1] < max_y

        playground_1.remove_agent(agent)


# Create an engine then add an agent
def test_engine(base_forward_agent_random):
    playground = SingleRoom(size=(200, 200))
    agent = base_forward_agent_random
    engine = Engine(playground, time_limit=100)
    playground.add_agent(agent)
    assert len(engine.agents) == 1
    playground.remove_agent(agent)
    assert len(engine.agents) == 0


# Run the playground, check that position changed
def test_engine_run(base_forward_agent_random):
    playground = SingleRoom(size=(200, 200))
    agent = base_forward_agent_random
    playground.add_agent(agent)
    engine = Engine(playground, time_limit=100)

    pos_start = agent.position
    engine.run()
    assert pos_start != agent.position

    playground.remove_agent(agent)
    playground.add_agent(agent)

    engine = Engine(playground, time_limit=100)
    assert len(engine.agents) == 1
    engine.run()

    playground.remove_agent(agent)
    engine = Engine(playground, time_limit=100)
    playground.add_agent(agent)
    assert len(engine.agents) == 1

    engine.run()


# Run all test playgrounds with basic non-interactive agent
def test_all_test_playgrounds(base_forward_agent_random, pg_test_class):

    agent = base_forward_agent_random

    playground = pg_test_class()

    playground.add_agent(agent, allow_overlapping=False)

    print('Starting testing of ', pg_test_class.__name__)

    engine = Engine(playground, time_limit=10000)
    engine.run()
    assert 0 < agent.position[0] < playground.size[0]
    assert 0 < agent.position[1] < playground.size[1]

    engine.terminate()
    playground.remove_agent(agent)


# Run all test playgrounds with basic interactive agent
def test_all_test_playgrounds_interactive(base_forward_agent_random, pg_test_class):

    agent = base_forward_agent_random

    playground = pg_test_class()

    playground.add_agent(agent, allow_overlapping=False)

    print('Starting testing of ', pg_test_class.__name__)

    engine = Engine(playground, time_limit=10000)
    engine.run()
    assert 0 < agent.position[0] < playground.size[0]
    assert 0 < agent.position[1] < playground.size[1]

    engine.terminate()
    playground.remove_agent(agent)


# Run all test playgrounds with 100 agents
def test_multiagents(pg_test_class):

    playground = pg_test_class()

    print('Starting Multiagent testing of ', pg_test_class.__name__)

    pos_area_sampler = playground.initial_agent_coordinates

    for _ in range(100):
        agent = BaseAgent(controller=RandomContinuous(), interactive=True)
        playground.add_agent(agent, pos_area_sampler)

    assert len(playground.agents) == 100

    engine = Engine(playground, time_limit=100, screen=False)
    engine.run(update_screen=False)
    engine.terminate()


# Run all test playgrounds with 4 agents
def test_multiagents_no_overlapping(pg_test_class):

    playground = pg_test_class()

    print('Starting Multiagent testing of ', pg_test_class.__name__)

    for _ in range(4):
        agent = BaseAgent(controller=RandomContinuous(), interactive=True)
        playground.add_agent(agent, allow_overlapping=False)

    assert len(playground.agents) == 4

    engine = Engine(playground, time_limit=100, screen=False)
    engine.run(update_screen=False)


# Run all test playgrounds with 10 agents
def test_multisteps(base_forward_agent_random, pg_test_class):

    agent = base_forward_agent_random
    sensor = Touch(name='touch_1', anchor=agent.base_platform)
    agent.add_sensor(sensor)

    playground = pg_test_class()
    print('Starting Multistep testing of ', pg_test_class.__name__)
    playground.add_agent(agent)

    engine = Engine(playground, time_limit=10000, screen=False)

    while engine.game_on:

        actions = {}
        for agent in engine.agents:
            actions[agent] = agent.controller.generate_actions()

        engine.multiple_steps(actions=actions, n_steps=3)
        engine.update_observations()

    engine.terminate()
    playground.remove_agent(agent)


def test_agent_in_different_environments(base_forward_agent_random):

    print('Testing of agent moving to different environments')

    agent = base_forward_agent_random
    pg_1 = SingleRoom((300, 300))
    pg_2 = SingleRoom((100, 100))

    # Play in pg 1
    pg_1.add_agent(agent)
    engine = Engine(pg_1, 100)
    engine.run()
    engine.terminate()
    pg_1.remove_agent(agent)

    # Play in pg 2
    pg_2.add_agent(agent)
    engine = Engine(pg_2, 100)
    engine.run()
    engine.terminate()
    pg_2.remove_agent(agent)

    # Alternate between playgrounds
    pg_1.reset()
    pg_2.reset()

    engine_1 = Engine(pg_1, 100)
    engine_2 = Engine(pg_2, 100)

    print('going to playground 1')
    pg_1.add_agent(agent)
    engine_1.run(10)
    pg_1.remove_agent(agent)

    print('going to playground 2')
    pg_2.add_agent(agent)
    engine_2.run(10)
    pg_2.remove_agent(agent)

    print('running playground 1 without agent')
    engine_1.run(10)
    assert engine_1.elapsed_time == 20

    print('agent returning to playground 1')
    pg_1.add_agent(agent)
    engine_1.run()
    engine_1.terminate()
    pg_1.remove_agent(agent)

    print('agent returning to playground 2')
    pg_2.add_agent(agent)
    engine_2.run()
    engine_2.terminate()
    pg_2.remove_agent(agent)

    print(' Fail when adding agent to 2 playgrounds ')
    pg_1.reset()
    pg_2.reset()
    pg_1.add_agent(agent)
