from simple_playgrounds.engine import Engine
from simple_playgrounds.playground.layouts import SingleRoom

from simple_playgrounds.element.elements.conditioning import ColorChanging, FlipReward
from simple_playgrounds.element.elements.activable import RewardOnActivation
from simple_playgrounds.common.timer import PeriodicTimer


def test_color_changing(base_forward_interactive_agent_external):
    playground = SingleRoom(size=(200, 200))

    agent = base_forward_interactive_agent_external

    color_1 = (100, 100, 0)
    color_2 = (0, 100, 100)
    color_3 = (20, 200, 2)
    colors = [color_1, color_2, color_3]
    durations = [3, 4, 5]

    elem = ColorChanging(textures=colors)

    playground.add_agent(agent, ((80, 100), 0))
    playground.add_element(elem, ((80 + agent.base_platform.radius + elem.radius + 2, 100), 0))

    timer = PeriodicTimer(durations=durations)

    playground.add_timer(timer, elem)

    engine = Engine(playground, time_limit=100)

    while engine.game_on:

        index_color = 0

        for d in durations:

            for _ in range(d):
                assert elem.texture.base_color == colors[index_color]
                engine.step()

            index_color += 1

        assert elem.texture.base_color == colors[0]


def test_reward_changer(reward, base_forward_interactive_agent_external):
    playground = SingleRoom(size=(200, 200))

    agent = base_forward_interactive_agent_external

    color_1 = (100, 100, 0)
    color_2 = (0, 100, 100)
    colors = [color_1, color_2]
    durations = [3, 4]

    roa = RewardOnActivation(reward=reward)
    change = FlipReward(textures=colors, element_changed=roa)
    timer = PeriodicTimer(durations=durations)

    playground.add_agent(agent, ((80, 100), 0))
    playground.add_element(roa, ((80 + agent.base_platform.radius + roa.radius + 2, 100), 0))
    playground.add_element(change, ((40, 40), 0))
    playground.add_timer(timer, change)

    engine = Engine(playground, time_limit=100)
    actions = {agent: {agent.activate: 1}}

    index_color = 0

    while engine.game_on:

        sign = 1

        for d in durations:

            for t in range(d-1):
                engine.step(actions)
                assert change.texture.base_color == colors[index_color]
                assert agent.reward == sign * reward



            sign *= -1
            index_color = (index_color + 1) % len(colors)

            engine.step(actions)

            assert change.texture.base_color == colors[index_color]
            assert agent.reward == sign * reward




