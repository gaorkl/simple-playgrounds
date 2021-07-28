from simple_playgrounds.engine import Engine
from simple_playgrounds.playgrounds.layouts import SingleRoom
from simple_playgrounds.agents.agents import BaseAgent
from simple_playgrounds.agents.parts.controllers import External

from simple_playgrounds.elements.collection.activable import Dispenser, RewardOnActivation, OpenCloseSwitch, TimerSwitch
from simple_playgrounds.elements.collection.contact import Candy
from simple_playgrounds.common.position_utils import CoordinateSampler
from simple_playgrounds.elements.collection.basic import Door

from simple_playgrounds.common.timer import Timer


def test_dispenser():
    playground = SingleRoom(size=(200, 200))

    agent = BaseAgent(
        controller=External(),
        interactive=True,
        rotate=False,
        lateral=False,
        backward=True,
    )

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


def test_dispenser_limit():
    playground = SingleRoom(size=(200, 200))

    agent = BaseAgent(
        controller=External(),
        interactive=True,
        rotate=False,
        lateral=False,
        backward=True,
    )

    dispenser = Dispenser(element_produced=Candy,
                          production_area=CoordinateSampler(center=(50, 100), area_shape='circle', radius=1),
                          production_limit=4,
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

    assert total_rew == 4


def test_reward_on_activation():
    playground = SingleRoom(size=(200, 200))

    agent = BaseAgent(
        controller=External(),
        interactive=True,
        rotate=False,
        lateral=False,
        backward=True,
    )

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


def test_openclose_switch():
    playground = SingleRoom(size=(200, 200))

    agent = BaseAgent(
        controller=External(),
        interactive=True,
        rotate=False,
        lateral=False,
        backward=True,
    )

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


def test_timer_switch():
    playground = SingleRoom(size=(200, 200))

    agent = BaseAgent(
        controller=External(),
        interactive=True,
        rotate=False,
        lateral=False,
        backward=True,
    )

    door = Door(start_point=(180, 180), end_point=(160, 160), door_depth=5)
    playground.add_element(door, ((150, 150), 0))

    switch_1 = TimerSwitch(door=door, invisible_range=40, timer=Timer(durations=5))
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

