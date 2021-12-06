from simple_playgrounds.engine import Engine
from simple_playgrounds.playground.layouts import SingleRoom

from simple_playgrounds.element.elements.zone import HealingZone, GoalZone


def test_reward_zone(base_forward_interactive_agent_external):
    playground = SingleRoom(size=(200, 200))

    agent = base_forward_interactive_agent_external

    healing_zone = HealingZone(reward=3, limit=31)
    playground.add_agent(agent, ((100, 100), 0))
    playground.add_element(healing_zone, ((100, 100), 0))

    engine = Engine(playground, time_limit=50)

    total_rew = 0

    while engine.game_on:
        engine.step()
        total_rew += agent.reward

    assert total_rew == 31


def test_termination_zone(base_forward_interactive_agent_external):
    playground = SingleRoom(size=(200, 200))

    agent = base_forward_interactive_agent_external

    goal = GoalZone(reward=100, size=(5, 5))
    playground.add_agent(agent, ((100, 100), 0))
    playground.add_element(goal, ((140, 100), 0))

    engine = Engine(playground, time_limit=100)

    actions = {agent: {agent.longitudinal_force: 1}}

    while engine.game_on:
        engine.step(actions)

    assert agent.reward > 0
    assert playground.done
