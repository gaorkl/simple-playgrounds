from simple_playgrounds.engine import Engine
from simple_playgrounds.playground.layouts import SingleRoom

from simple_playgrounds.element.elements.activable import Dispenser, RewardOnActivation, OpenCloseSwitch, TimerSwitch
from simple_playgrounds.element.elements.edible import Apple
from simple_playgrounds.element.elements.contact import Candy
from simple_playgrounds.common.position_utils import CoordinateSampler
from simple_playgrounds.element.elements.basic import Door

from simple_playgrounds.common.timer import CountDownTimer


def test_dispenser(base_forward_interactive_agent_external):
    playground = SingleRoom(size=(200, 200))

    agent = base_forward_interactive_agent_external

    dispenser = Dispenser(element_produced=Candy,
                          production_area=CoordinateSampler(center=(50, 100), area_shape='circle', radius=1),
                          invisible_range=40)

    playground.add_agent(agent, ((100, 100), 0))
    playground.add_element(dispenser, ((140, 100), 0))

    engine = Engine(playground, time_limit=100)

    total_rew = 0

    while engine.game_on:

        if engine.elapsed_time < 50:
            actions = {agent: {agent.activate: 1}}

        else:
            actions = {agent: {agent.longitudinal_force: -1.}}
        engine.step(actions)
        total_rew += agent.reward

    assert total_rew > 0


def test_dispenser_limit(base_forward_interactive_agent_external):
    playground = SingleRoom(size=(200, 200))

    agent = base_forward_interactive_agent_external

    dispenser = Dispenser(element_produced=Candy,
                          production_area=CoordinateSampler(center=(50, 100), area_shape='circle', radius=10),
                          production_limit=1,
                          invisible_range=40,
                          element_produced_params={'reward': 1})

    playground.add_agent(agent, ((100, 100), 0))
    playground.add_element(dispenser, ((140, 100), 0))

    engine = Engine(playground, time_limit=100)

    total_rew = 0

    while engine.game_on:

        if engine.elapsed_time < 50:
            actions = {agent: {agent.activate: 1}}

        else:
            actions = {agent: {agent.longitudinal_force: -1.}}
        engine.step(actions)
        total_rew += agent.reward

    assert total_rew == 1


def test_reward_on_activation(base_forward_interactive_agent_external):
    playground = SingleRoom(size=(200, 200))

    agent = base_forward_interactive_agent_external

    roa = RewardOnActivation(reward=5, quantity_rewards=10, invisible_range=40)

    playground.add_agent(agent, ((100, 100), 0))
    playground.add_element(roa, ((140, 100), 0))

    engine = Engine(playground, time_limit=100)

    total_rew = 0
    actions = {agent: {agent.activate: 1}}

    while engine.game_on:

        engine.step(actions)
        total_rew += agent.reward

    assert total_rew == 50


def test_openclose_switch(base_forward_interactive_agent_external):
    playground = SingleRoom(size=(200, 200))

    agent = base_forward_interactive_agent_external

    door = Door(start_point=(180, 180), end_point=(160, 160), door_depth=5)
    playground.add_element(door, ((150, 150), 0))

    switch_1 = OpenCloseSwitch(door=door, invisible_range=40)
    playground.add_element(switch_1, ((140, 100), 0))

    playground.add_agent(agent, ((100, 100), 0))

    engine = Engine(playground, time_limit=100)
    actions = {agent: {agent.activate: 1}}

    engine.step(actions)
    assert door not in playground.elements

    engine.step(actions)
    assert door in playground.elements

    engine.step(actions)
    assert door not in playground.elements

    engine.step(actions)
    assert door in playground.elements


def test_timer_switch(base_forward_interactive_agent_external):
    playground = SingleRoom(size=(200, 200))

    agent = base_forward_interactive_agent_external

    door = Door(start_point=(180, 180), end_point=(160, 160), door_depth=5)
    playground.add_element(door, ((150, 150), 0))

    timer = CountDownTimer(duration=10)
    switch_1 = TimerSwitch(door=door, invisible_range=40, timer=timer)
    playground.add_element(switch_1, ((140, 100), 0))
    playground.add_timer(timer, switch_1)

    playground.add_agent(agent, ((100, 100), 0))

    engine = Engine(playground, time_limit=100)
    actions = {agent: {agent.activate: 1}}

    assert door in playground.elements

    # Open a first time
    engine.step(actions)
    assert door not in playground.elements

    for i in range(9):
        engine.step()
        assert door not in playground.elements

    engine.step()
    assert door in playground.elements

    # Open a second time
    engine.step(actions)
    assert door not in playground.elements

    for i in range(9):
        engine.step()
        assert door not in playground.elements

    engine.step()
    assert door in playground.elements

    # Open multiple time time
    engine.step(actions)
    engine.step(actions)
    engine.step(actions)
    engine.step(actions)
    assert door not in playground.elements

    for i in range(9):
        engine.step()
        assert door not in playground.elements

    engine.step()
    assert door in playground.elements


def test_edible_apple(base_forward_interactive_agent_external):
    playground = SingleRoom(size=(200, 200))

    agent = base_forward_interactive_agent_external

    apple = Apple(reward=16, shrink_ratio=0.5, invisible_range=30*16, min_reward=1)

    playground.add_agent(agent, ((100, 100), 0))
    playground.add_element(apple, ((140, 100), 0))

    engine = Engine(playground, time_limit=100)

    actions = {agent: {agent.activate: 1}}

    for rew in [16, 8, 4, 2, 1]:

        engine.step(actions)
        assert agent.reward == rew

    engine.step(actions)
    assert agent.reward == 0
    assert apple not in playground.elements

    engine.reset()

    for rew in [16, 8, 4, 2, 1]:
        engine.step(actions)
        assert agent.reward == rew

    engine.step(actions)
    assert agent.reward == 0
    assert apple not in playground.elements

