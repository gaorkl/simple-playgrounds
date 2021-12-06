from simple_playgrounds.engine import Engine
from simple_playgrounds.playground.layouts import SingleRoom

from simple_playgrounds.element.elements.contact import Candy, VisibleEndGoal, ContactSwitch
from simple_playgrounds.element.elements.basic import Door


def test_contact_candy(base_forward_interactive_agent_external):
    playground = SingleRoom(size=(200, 200))

    agent = base_forward_interactive_agent_external

    candy = Candy(reward=12)
    playground.add_agent(agent, ((60, 100), 0))
    playground.add_element(candy, ((160, 100), 0))

    engine = Engine(playground, time_limit=100)

    total_rew = 0
    actions = {agent: {agent.longitudinal_force: 1}}

    while engine.game_on:
        engine.step(actions)
        total_rew += agent.reward

    assert total_rew > 0


def test_contact_termination(base_forward_interactive_agent_external):
    playground = SingleRoom(size=(200, 200))

    agent = base_forward_interactive_agent_external

    goal = VisibleEndGoal(reward=100)
    playground.add_agent(agent, ((100, 100), 0))
    playground.add_element(goal, ((140, 100), 0))

    engine = Engine(playground, time_limit=100)

    total_rew = 0
    actions = {agent: {agent.longitudinal_force: 1}}

    while engine.game_on:
        engine.step(actions)
        total_rew += agent.reward

    assert total_rew > 0
    assert playground.done


def test_lock_key_door(base_forward_interactive_agent_external):
    playground = SingleRoom(size=(200, 200))

    agent = base_forward_interactive_agent_external

    playground.add_agent(agent, ((80, 100), 0))

    door = Door(start_point=(180, 180), end_point=(160, 160), door_depth=5)
    playground.add_element(door)

    switch = ContactSwitch(door=door)
    playground.add_element(switch, ((140, 100), 0))

    engine = Engine(playground, time_limit=200)

    # agent grasps and move forward
    actions = {agent: { agent.longitudinal_force: 1}}

    while engine.game_on:

        engine.step(actions)

    assert door not in playground.elements

    # agent stands still

    engine.reset()
    assert door in playground.elements

    while engine.game_on:
        engine.step()

    assert door in playground.elements

