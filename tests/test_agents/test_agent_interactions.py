import pytest
from simple_playgrounds.agent.controller import ContinuousController, DiscreteController, RangeController

import numpy as np
from simple_playgrounds.playground.playground import EmptyPlayground
from tests.mock_agents import MockAgent, MockBase
from tests.mock_entities import MockBarrier, MockPhysical, MockZoneTriggered, trigger_triggers_triggered
from simple_playgrounds.entity.embodied.contour import Contour
from simple_playgrounds.common.definitions import CollisionTypes

coord_obst = (40, 0), 0


def test_agent_barrier_no_team():

    playground = EmptyPlayground()
    agent = MockAgent(playground)

    contour_barrier = Contour(shape='rectangle', size=(10, 400))
    barrier = MockBarrier(playground, coord_obst, contour=contour_barrier)

    commands = {agent: {agent._base.forward_controller: 1}}
    
    assert agent.position == (0, 0)

    for _ in range(1000):
        playground.step(commands=commands)

    assert agent.position.x > 0
    assert agent.position.x > 40


def test_agent_team_barrier_no_team():

    playground = EmptyPlayground()
    agent = MockAgent(playground, teams='test')

    assert agent._base._teams == ['test']

    contour_barrier = Contour(shape='rectangle', size=(10, 400))
    barrier = MockBarrier(playground, coord_obst, contour=contour_barrier)

    commands = {agent: {agent._base.forward_controller: 1}}
    
    assert agent.position == (0, 0)

    for _ in range(1000):
        playground.step(commands=commands)

    assert agent.position.x > 0
    assert agent.position.x < 40


def test_agent_team_barrier_team():

    playground = EmptyPlayground()
    agent = MockAgent(playground, teams='test_1')

    assert agent._base._teams == ['test_1']

    contour_barrier = Contour(shape='rectangle', size=(10, 400))
    barrier = MockBarrier(playground, coord_obst, contour=contour_barrier, teams=['test_2'])

    commands = {agent: {agent._base.forward_controller: 1}}
    
    assert agent.position == (0, 0)

    for _ in range(1000):
        playground.step(commands=commands)

    assert agent.position.x > 0
    assert agent.position.x < 40

def test_agent_movable():

    playground = EmptyPlayground()
    agent = MockAgent(playground)

    contour_obstacle = Contour(shape='square', radius=20)
    obstacle = MockPhysical(playground, coord_obst, contour=contour_obstacle, movable=True, mass=5)

    commands = {agent: {agent._base.forward_controller: 1}}
    
    assert agent.position == (0, 0)

    for _ in range(1000):
        playground.step(commands=commands)

    assert obstacle.coordinates != coord_obst

    playground.reset()

    assert agent.position == (0, 0)
    assert obstacle.coordinates == coord_obst


def test_agent_traversable():

    playground = EmptyPlayground()
    agent = MockAgent(playground)

    contour_barrier = Contour(shape='rectangle', size=(10, 400))
    MockPhysical(playground, coord_obst, contour=contour_barrier, traversable=True)

    commands = {agent: {agent._base.forward_controller: 1}}
    
    assert agent.position == (0, 0)

    for _ in range(1000):
        playground.step(commands=commands)

    assert agent.position.x > 0
    assert agent.position.x > 40


def test_agent_interacts():

    playground = EmptyPlayground()
    playground.add_interaction(CollisionTypes.TEST_TRIGGER, CollisionTypes.TEST_TRIGGERED, trigger_triggers_triggered)

    agent = MockAgent(playground, teams='team_1')

    contour_zone = Contour(shape='circle', radius=100)
    zone_1 = MockZoneTriggered(playground, coord_obst, contour=contour_zone, teams='team_1')
    zone_2 = MockZoneTriggered(playground, coord_obst, contour=contour_zone, teams='team_2')
    zone_3 = MockZoneTriggered(playground, coord_obst, contour=contour_zone)

    playground.step()

    assert zone_1.activated
    assert not zone_2.activated
    assert not zone_3.activated

    

