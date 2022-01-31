
import math

import pytest
from simple_playgrounds.agent.part.part import AnchoredPart
from simple_playgrounds.entity.embodied.contour import Contour
from tests.mock_agents import MockAgent, MockAnchoredPart
from simple_playgrounds.playground.playground import EmptyPlayground


@pytest.fixture(scope='module', params=[(20, 20), (-20, -20), (0, 0)])
def pos(request):
    return request.param

@pytest.fixture(scope='module', params=[-1, 0, 6])
def angle(request):
    return request.param

@pytest.fixture(scope='module', params=[-1, 0, 6])
def offset_angle(request):
    return request.param

@pytest.fixture(scope='module', params=[(10, 10), (-10, -10), (0,0)])
def pos_on_part(request):
    return request.param

@pytest.fixture(scope='module', params=[(10, 10), (-10, -10), (0,0)])
def pos_on_anchor(request):
    return request.param


def test_add_part(pos, angle, pos_on_part, pos_on_anchor, offset_angle):

    playground = EmptyPlayground()
    agent = MockAgent(playground, coordinates=(pos, angle))

    contour = Contour(shape='rectangle', size=(10, 30))
    part = MockAnchoredPart(agent._base,
                            pivot_position_on_part=pos_on_part,
                            pivot_position_on_anchor=pos_on_anchor,
                            relative_angle=offset_angle,
                            rotation_range=math.pi,
                            contour=contour,
                            )

    assert agent._base.position == pos
    
    agent.move_to(((0, 0), 0))
    assert part.position == pos_on_anchor + (-pos_on_part).rotate(-offset_angle)



