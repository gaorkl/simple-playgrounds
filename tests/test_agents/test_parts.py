
import math
import pymunk
import random
import pdb

import pytest
from simple_playgrounds.agent.part.part import AnchoredPart
from simple_playgrounds.entity.embodied.contour import Contour
from tests.mock_agents import MockAgent, MockAnchoredPart
from simple_playgrounds.playground.playground import EmptyPlayground


@pytest.fixture(scope='module', params=[(20, 20), (-20, -20), (0, 0)])
def pos(request):
    return request.param


@pytest.fixture(scope='module', params=[-4,  0, 1])
def angle(request):
    return request.param


@pytest.fixture(scope='module', params=[-4, 0, 1])
def offset_angle(request):
    return request.param


@pytest.fixture(scope='module', params=[(10, 10), (-10, -10), (0, 0)])
def pos_on_part(request):
    return request.param


@pytest.fixture(scope='module', params=[(10, 10), (-10, -10), (0, 0)])
def pos_on_anchor(request):
    return request.param


def test_move(pos, angle, pos_on_part, pos_on_anchor, offset_angle):

    playground = EmptyPlayground()
    agent = MockAgent(playground, coordinates=(pos, angle))

    contour = Contour(shape='rectangle', size=(50, 30))
    part = MockAnchoredPart(agent._base,
                            pivot_position_on_part=pos_on_part,
                            pivot_position_on_anchor=pos_on_anchor,
                            relative_angle=offset_angle,
                            rotation_range=math.pi,
                            contour=contour,
                            )

    # Check that joints are correct. Agent shouldn't move
    for _ in range(100):
        playground.step()

    assert math.isclose(agent.position.x, pos[0], abs_tol=1e-10)
    assert math.isclose(agent.position.y, pos[1], abs_tol=1e-10)

    part_pos = (pymunk.Vec2d(*pos)
                + pymunk.Vec2d(*pos_on_anchor).rotated(angle)
                - pymunk.Vec2d(*pos_on_part).rotated(angle+offset_angle))

    assert math.isclose(part.position.x, part_pos.x)
    assert math.isclose(part.position.y, part_pos.y)

    random_pos = (random.uniform(-10, 10), random.uniform(-10, 10))
    random_angle = random.uniform(-10, 10)
    agent.move_to((random_pos, random_angle))

    for _ in range(100):
        playground.step()

    part_pos_after_move = (pymunk.Vec2d(*random_pos)
                + pymunk.Vec2d(*pos_on_anchor).rotated(random_angle)
                - pymunk.Vec2d(*pos_on_part).rotated(random_angle+offset_angle))

    assert math.isclose(part.position.x, part_pos_after_move.x)
    assert math.isclose(part.position.y, part_pos_after_move.y)

def test_reset_position(pos, angle, pos_on_part, pos_on_anchor, offset_angle):
    playground = EmptyPlayground()
    agent = MockAgent(playground, coordinates=(pos, angle))

    contour = Contour(shape='rectangle', size=(50, 30))
    part = MockAnchoredPart(agent._base,
                            pivot_position_on_part=pos_on_part,
                            pivot_position_on_anchor=pos_on_anchor,
                            relative_angle=offset_angle,
                            rotation_range=math.pi,
                            contour=contour,
                            )

    random_pos = (random.uniform(-10, 10), random.uniform(-10, 10))
    random_angle = random.uniform(-10, 10)
    agent.move_to((random_pos, random_angle))

    for _ in range(100):
        playground.step()

    part_pos_after_move = (pymunk.Vec2d(*random_pos)
                + pymunk.Vec2d(*pos_on_anchor).rotated(random_angle)
                - pymunk.Vec2d(*pos_on_part).rotated(random_angle+offset_angle))

    assert math.isclose(part.position.x, part_pos_after_move.x)
    assert math.isclose(part.position.y, part_pos_after_move.y)

    playground.reset()

    assert math.isclose(agent.position.x, pos[0], abs_tol=1e-10)
    assert math.isclose(agent.position.y, pos[1], abs_tol=1e-10)
   

def test_command_and_reset(pos, angle, pos_on_part, pos_on_anchor, offset_angle):
    playground = EmptyPlayground()
    agent = MockAgent(playground, coordinates=(pos, angle))

    contour = Contour(shape='rectangle', size=(50, 30))
    part = MockAnchoredPart(agent._base,
                            pivot_position_on_part=pos_on_part,
                            pivot_position_on_anchor=pos_on_anchor,
                            relative_angle=offset_angle,
                            rotation_range=math.pi,
                            contour=contour,
                            )

    command_list = [{agent: {agent._base.forward_controller: random.uniform(-1, 1), 
                             part.joint_controller: random.uniform(-1, 1)
                             }
                     } for _ in range(100)]

    for command in command_list:
        playground.step(commands=command)
   
    assert not math.isclose(agent.position.x, pos[0], abs_tol=1e-10)
    assert not math.isclose(agent.position.y, pos[1], abs_tol=1e-10)
    
    playground.reset()

    playground.step()

    assert math.isclose(agent.position.x, pos[0], abs_tol=1e-10)
    assert math.isclose(agent.position.y, pos[1], abs_tol=1e-10)
    
    part_pos = (pymunk.Vec2d(*pos)
                + pymunk.Vec2d(*pos_on_anchor).rotated(angle)
                - pymunk.Vec2d(*pos_on_part).rotated(angle+offset_angle))

    assert math.isclose(part.position.x, part_pos.x)
    assert math.isclose(part.position.y, part_pos.y)

def test_move_after_command():

    playground = EmptyPlayground()
    agent = MockAgent(playground)

    contour = Contour(shape='rectangle', size=(50, 30))
    part = MockAnchoredPart(agent._base,
                            pivot_position_on_part=(10, 10),
                            pivot_position_on_anchor=(-10, -5),
                            relative_angle=math.pi/4,
                            rotation_range=math.pi,
                            contour=contour,
                            )

    command_list = [{agent: {agent._base.forward_controller: random.uniform(-1, 1), 
                             part.joint_controller: random.uniform(-1, 1)
                             }
                     } for _ in range(100)]

    for command in command_list:
        playground.step(commands=command)
 
    assert part.relative_angle != part._angle_offset
    rel_angle = part.relative_angle % (2*math.pi)
    rel_pos = part.relative_position

    # Move to random position and odn't keep velocities.
    # Check that relative position and angle is not changed
    random_pos = (random.uniform(-10, 10), random.uniform(-10, 10))
    random_angle = random.uniform(-10, 10)
    agent.move_to((random_pos, random_angle), keep_velocity=False)

    pdb.set_trace()

    playground.step()

    assert math.isclose(rel_angle, part.relative_angle % (2*math.pi))

    assert math.isclose(part.relative_position.x, rel_pos.x, abs_tol=1e-10)
    assert math.isclose(part.relative_position.y, rel_pos.y, abs_tol=1e-10)

    # Move to random position but don't keep joints. 
    # Check that relative position and angle are changed
    random_pos = (random.uniform(-10, 10), random.uniform(-10, 10))
    random_angle = random.uniform(-10, 10)
    agent.move_to((random_pos, random_angle), keep_joints=False, keep_velocity=False)

    playground.step()

    assert math.isclose(part._angle_offset % (2*math.pi), part.relative_angle % (2*math.pi))

    assert not math.isclose(part.relative_position.x, rel_pos.x, abs_tol=1e-10)
    assert not math.isclose(part.relative_position.y, rel_pos.y, abs_tol=1e-10)


# def test_move_keep_velocities():

#     playground = EmptyPlayground()
#     agent = MockAgent(playground)

#     contour = Contour(shape='rectangle', size=(50, 30))
#     part = MockAnchoredPart(agent._base,
#                             pivot_position_on_part=(10, 10),
#                             pivot_position_on_anchor=(-10, -5),
#                             relative_angle=math.pi/4,
#                             rotation_range=math.pi,
#                             contour=contour,
#                             )

#     command_list = [{agent: {agent._base.forward_controller: random.uniform(-1, 1), 
#                              part.joint_controller: random.uniform(-1, 1)
#                              }
#                      } for _ in range(100)]

#     for command in command_list:
#         playground.step(commands=command)
 
#     assert part.relative_angle != part._angle_offset
#     rel_angle = part.relative_angle % (2*math.pi)
#     rel_pos = part.relative_position

#     # Move to random position. Check that relative position and angle is not changed
#     random_pos = (random.uniform(-10, 10), random.uniform(-10, 10))
#     random_angle = random.uniform(-10, 10)
#     agent.move_to((random_pos, random_angle))

#     assert math.isclose(rel_angle, part.relative_angle % (2*math.pi))

#     assert math.isclose(part.relative_position.x, rel_pos.x, abs_tol=1e-10)
#     assert math.isclose(part.relative_position.y, rel_pos.y, abs_tol=1e-10)

#     # Move to random position but don't keep joints. 
#     # Check that relative position and angle are changed
#     random_pos = (random.uniform(-10, 10), random.uniform(-10, 10))
#     random_angle = random.uniform(-10, 10)
#     agent.move_to((random_pos, random_angle), keep_joints=False)

#     assert math.isclose(part._angle_offset % (2*math.pi), part.relative_angle % (2*math.pi))

#     assert not math.isclose(part.relative_position.x, rel_pos.x, abs_tol=1e-10)
#     assert not math.isclose(part.relative_position.y, rel_pos.y, abs_tol=1e-10)

