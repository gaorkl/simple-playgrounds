from simple_playgrounds.engine import Engine
from simple_playgrounds.playground.layouts import SingleRoom

from simple_playgrounds.element.elements.activable import VendingMachine, Chest, Lock
from simple_playgrounds.element.elements.gem import Coin, Key
from simple_playgrounds.element.elements.contact import Candy
from simple_playgrounds.element.elements.basic import Door


def test_vending_machine(base_forward_interactive_agent_external):
    playground = SingleRoom(size=(200, 200))

    agent = base_forward_interactive_agent_external

    playground.add_agent(agent, ((80, 100), 0))

    vending = VendingMachine(quantity_rewards=3, reward=10)
    playground.add_element(vending, ((140, 100), 0))

    coin = Coin(graspable=True, vending_machine=vending, radius=5)
    playground.add_element(coin, ((80 + agent.base_platform.radius + coin.radius + 2, 100), 0))

    engine = Engine(playground, time_limit=100)

    # agent grasps and move forward

    total_rew = 0

    actions = {agent: {agent.grasp: 1, agent.longitudinal_force: 1}}

    while engine.game_on:
        engine.step(actions)
        total_rew += agent.reward
    assert total_rew == 10
    assert not agent.grasped_elements

    engine.step(actions)
    assert not agent.grasped_elements

    # test reset
    engine.reset()
    total_rew = 0

    while engine.game_on:
        actions = {agent: {agent.grasp: 1, agent.longitudinal_force: 1}}
        engine.step(actions)
        total_rew += agent.reward

    assert total_rew > 0

    # agent stands still

    engine.reset()
    total_rew = 0

    while engine.game_on:
        engine.step()
        total_rew += agent.reward

    assert total_rew == 0


def test_chest(base_forward_interactive_agent_external):
    playground = SingleRoom(size=(200, 200))

    agent = base_forward_interactive_agent_external

    playground.add_agent(agent, ((80, 100), 0))

    chest = Chest(treasure=Candy())
    playground.add_element(chest, ((140, 100), 0))

    key = Key(graspable=True, locked_elem=chest, radius=5)
    playground.add_element(key, ((80 + agent.base_platform.radius + key.radius + 2, 100), 0))

    engine = Engine(playground, time_limit=200)

    # agent grasps and move forward

    total_rew = 0

    while engine.game_on:

        actions = {agent: {agent.grasp: 1, agent.longitudinal_force: 1}}
        engine.step(actions)
        total_rew += agent.reward

    assert total_rew > 0

    # agent stands still

    engine.reset()
    total_rew = 0

    while engine.game_on:
        engine.step()
        total_rew += agent.reward

    assert total_rew == 0


def test_lock_key_door(base_forward_interactive_agent_external):
    playground = SingleRoom(size=(200, 200))

    agent = base_forward_interactive_agent_external

    playground.add_agent(agent, ((80, 100), 0))

    door = Door(start_point=(180, 180), end_point=(160, 160), door_depth=5)
    playground.add_element(door)

    lock = Lock(door)
    playground.add_element(lock, ((140, 100), 0))

    key = Key(graspable=True, locked_elem=lock, radius=5)
    playground.add_element(key, ((80 + agent.base_platform.radius + key.radius + 2, 100), 0))

    engine = Engine(playground, time_limit=200)

    # agent grasps and move forward

    while engine.game_on:

        actions = {agent: {agent.grasp: 1, agent.longitudinal_force: 1}}
        engine.step(actions)

    assert door not in playground.elements

    # agent stands still

    engine.reset()
    assert door in playground.elements

    while engine.game_on:
        engine.step()

    assert door in playground.elements
