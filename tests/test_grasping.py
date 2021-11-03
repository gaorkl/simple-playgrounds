import numpy as np

from simple_playgrounds.engine import Engine
from simple_playgrounds.playground.layouts import SingleRoom
from simple_playgrounds.agent.agents import BaseAgent
from simple_playgrounds.agent.controllers import External

from simple_playgrounds.element.elements.basic import Physical

from simple_playgrounds.device.sensors.robotic import RgbCamera


def test_grasping():

    playground = SingleRoom(size=(200, 200))

    agent_1 = BaseAgent(
        controller=External(),
        interactive=True,
        rotate=True,
        lateral=False,
        radius=10,
    )
    playground.add_agent(agent_1, ((100, 100), 0))

    elem = Physical(config_key='circle', mass=5, radius=10, graspable=True)
    initial_position_elem = ((100 + agent_1.base_platform.radius + elem.radius + 2, 100), 0)
    playground.add_element(elem, initial_position_elem)

    engine = Engine(playground)

    actions = {agent_1: {agent_1.grasp: 1, agent_1.rotation_velocity: 1}}
    engine.step(actions)
    engine.step(actions)

    assert (elem.position, elem.angle) != initial_position_elem
    assert elem.held_by[0].part.agent is agent_1

    engine.step()
    assert not elem.held_by


def test_grasping_non_graspable():

    playground = SingleRoom(size=(200, 200))

    agent_1 = BaseAgent(
        controller=External(),
        interactive=True,
        rotate=True,
        lateral=False,
        radius=10,
    )
    playground.add_agent(agent_1, ((100, 100), 0))

    elem = Physical(config_key='circle', mass=5, radius=10, graspable=False)
    initial_position_elem = ((100 + agent_1.base_platform.radius + elem.radius + 2, 100), 0)
    playground.add_element(elem, initial_position_elem)

    engine = Engine(playground)

    actions = {agent_1: {agent_1.grasp: 1, agent_1.rotation_velocity: 1}}
    engine.step(actions)
    engine.step(actions)

    assert ( elem.position, elem.angle) == initial_position_elem


def test_grasping_sensor():

    playground = SingleRoom(size=(200, 200))

    agent_1 = BaseAgent(
        controller=External(),
        interactive=True,
        rotate=True,
        lateral=False,
        radius=10,
    )

    rgb = RgbCamera(anchor=agent_1.base_platform)
    agent_1.add_sensor(rgb)

    playground.add_agent(agent_1, ((100, 100), 0))

    elem = Physical(config_key='circle', mass=5, radius=10, graspable=True)
    initial_position_elem = ((100 + agent_1.base_platform.radius + elem.radius + 2, 100), 0)
    playground.add_element(elem, initial_position_elem)

    engine = Engine(playground)
    engine.step()
    engine.update_observations()
    obs_1 = rgb.sensor_values[:]

    actions = {agent_1: {agent_1.grasp: 1}}
    engine.step(actions)
    engine.update_observations()
    obs_2 = rgb.sensor_values[:]

    engine.update_observations(grasped_invisible=True)
    obs_3 = rgb.sensor_values[:]

    assert (obs_1 == obs_2).all()
    assert (obs_3 != obs_1).any()

    playground.remove_add_within(elems_remove=[elem], elems_add=[])
    engine.step()
    engine.update_observations()
    obs_4 = rgb.sensor_values[:]

    assert (obs_4 == obs_3).all()

