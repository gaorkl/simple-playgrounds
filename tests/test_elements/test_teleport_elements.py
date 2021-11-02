import math

from simple_playgrounds.engine import Engine
from simple_playgrounds.playground.layouts import SingleRoom
from simple_playgrounds.element.elements.teleport import InvisibleBeam, VisibleBeamHoming, Portal, PortalColor
from simple_playgrounds.common.position_utils import CoordinateSampler

from simple_playgrounds.element.elements.basic import Physical


def test_beam(base_forward_interactive_agent_external):
    playground = SingleRoom(size=(200, 200))
    agent = base_forward_interactive_agent_external
    beam = InvisibleBeam(destination=((50, 50), 0))

    playground.add_agent(agent, ((100, 100), 0))
    playground.add_element(beam, ((140, 100), 0))

    engine = Engine(playground, time_limit=100)

    actions = {agent: {agent.longitudinal_force: 1}}

    while engine.game_on:

        engine.step(actions)

    assert agent.position[1] == 50

    engine.terminate()


def test_beam_orientation(base_forward_interactive_agent_external):
    playground = SingleRoom(size=(200, 200))
    agent = base_forward_interactive_agent_external
    beam = InvisibleBeam(destination=((50, 50), math.pi/2))

    playground.add_agent(agent, ((100, 100), 0))
    playground.add_element(beam, ((140, 100), 0))

    engine = Engine(playground, time_limit=100)

    actions = {agent: {agent.longitudinal_force: 1}}

    while engine.game_on:
        engine.step(actions)

    assert agent.position[0] == 50

    engine.terminate()


def test_beam_area(base_forward_interactive_agent_external):
    playground = SingleRoom(size=(200, 200))
    agent = base_forward_interactive_agent_external

    area = CoordinateSampler(center=(50, 50), area_shape='rectangle', size=(20, 20))

    beam = InvisibleBeam(destination=area)

    playground.add_agent(agent, ((100, 100), 0))
    playground.add_element(beam, ((140, 100), 0))

    engine = Engine(playground, time_limit=100)

    actions = {agent: {agent.longitudinal_force: 1}}

    while not agent.has_teleported:
        engine.step(actions)

    assert 30 <= agent.position[0] <= 80
    assert 30 <= agent.position[1] <= 80


def test_beam_homing(base_forward_interactive_agent_external):

    playground = SingleRoom(size=(200, 200))
    agent = base_forward_interactive_agent_external

    destination = Physical(config_key='pentagon')
    playground.add_element(destination, ((70, 70), 0))

    beam = VisibleBeamHoming(destination=destination, invisible_range=4)

    playground.add_agent(agent, ((100, 100), 0))
    playground.add_element(beam, ((140, 100), 0))

    engine = Engine(playground, time_limit=100)

    actions = {agent: {agent.longitudinal_force: 1}}

    while not agent.has_teleported:
        engine.step(actions)

    assert agent.position.get_distance(destination.position) < agent.base_platform.radius + destination.radius + 4 + 3


def test_portal(base_forward_interactive_agent_external):

    playground = SingleRoom(size=(200, 200))
    agent = base_forward_interactive_agent_external

    portal_1 = Portal(color=PortalColor.RED)
    portal_2 = Portal(color=PortalColor.BLUE)
    portal_3 = Portal(color=PortalColor.GREEN)
    portal_4 = Portal(color=(50, 50, 50))

    playground.add_agent(agent, ((100, 80), 0))
    playground.add_element(portal_1, ((140, 80), math.pi))
    playground.add_element(portal_2, ((50, 50), math.pi/2))
    playground.add_element(portal_3, ((50, 120), -math.pi/2))
    playground.add_element(portal_4, ((150, 160), math.pi))

    portal_1.destination = portal_2
    portal_3.destination = portal_4

    engine = Engine(playground, time_limit=1000)

    actions = {agent: {agent.longitudinal_force: 1}}

    while engine.game_on:
        engine.step(actions)

    assert agent.position[1] == 160
    assert agent.angle % (2 * math.pi) == math.pi
