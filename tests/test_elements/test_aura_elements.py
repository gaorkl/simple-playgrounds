from simple_playgrounds.engine import Engine
from simple_playgrounds.playground.layouts import SingleRoom
from simple_playgrounds.element.elements.aura import Fairy, Fireball


def test_fairy(base_forward_interactive_agent_external):
    playground = SingleRoom(size=(200, 200))

    agent = base_forward_interactive_agent_external

    fairy = Fairy(reward=4, total_reward=50)
    playground.add_agent(agent, ((100, 100), 0))
    playground.add_element(fairy, ((80 + agent.base_platform.radius + fairy.radius + 2, 100), 0))

    engine = Engine(playground, time_limit=100)
    actions = {agent: {agent.activate: 1}}

    total_rew = 0

    while engine.game_on:

        engine.step(actions)

        if engine.elapsed_time < 10:
            assert agent.reward == 4

        total_rew += agent.reward

    assert total_rew == 50

    # After reset
    engine.reset()

    total_rew = 0

    while engine.game_on:

        engine.step(actions)

        if engine.elapsed_time < 10:
            assert agent.reward == 4

        total_rew += agent.reward

    assert total_rew == 50


def test_fairy_no_limit(base_forward_interactive_agent_external):
    playground = SingleRoom(size=(200, 200))

    agent = base_forward_interactive_agent_external

    fairy = Fairy(reward=4)
    playground.add_agent(agent, ((100, 100), 0))
    playground.add_element(fairy, ((80 + agent.base_platform.radius + fairy.radius + 2, 100), 0))

    engine = Engine(playground, time_limit=100)
    actions = {agent: {agent.activate: 1}}

    total_rew = 0

    while engine.game_on:

        engine.step(actions)
        total_rew += agent.reward

    assert total_rew == 400


def test_fireball(base_forward_interactive_agent_external):
    playground = SingleRoom(size=(200, 200))

    agent = base_forward_interactive_agent_external

    fairy = Fireball(reward=-2, total_reward=-33)
    playground.add_agent(agent, ((100, 100), 0))
    playground.add_element(fairy, ((80 + agent.base_platform.radius + fairy.radius + 2, 100), 0))

    engine = Engine(playground, time_limit=100)
    actions = {agent: {agent.activate: 1}}

    total_rew = 0

    while engine.game_on:

        engine.step(actions)

        if engine.elapsed_time < 10:
            assert agent.reward == -2

        total_rew += agent.reward

    assert total_rew == -33

    # After reset
    engine.reset()

    total_rew = 0

    while engine.game_on:

        engine.step(actions)

        if engine.elapsed_time < 10:
            assert agent.reward == -2

        total_rew += agent.reward

    assert total_rew == -33

