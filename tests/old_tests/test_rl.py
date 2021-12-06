from simple_playgrounds.engine import Engine


def test_all_rl_playgrounds(base_forward_agent_random, pg_rl_class):

    agent = base_forward_agent_random

    playground = pg_rl_class()

    playground.add_agent(agent, allow_overlapping=False)

    print('Starting testing of ', pg_rl_class.__name__)

    engine = Engine(playground, time_limit=1000)
    engine.run()
    assert 0 < agent.position[0] < playground.size[0]
    assert 0 < agent.position[1] < playground.size[1]

    engine.terminate()
    playground.remove_agent(agent)
