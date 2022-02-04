
import math
import pymunk
import random
import pdb
import numpy as np
import pytest
from simple_playgrounds.agent.part.part import AnchoredPart
from simple_playgrounds.common.position_utils import CoordinateSampler, FixedCoordinateSampler
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


@pytest.fixture(scope='module', params=[True, False])
def keep_velocity(request):
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

    playground.step()

    part_pos_after_move = (pymunk.Vec2d(*random_pos)
                + pymunk.Vec2d(*pos_on_anchor).rotated(random_angle)
                - pymunk.Vec2d(*pos_on_part).rotated(random_angle+offset_angle))

    assert math.isclose(part.position.x, part_pos_after_move.x)
    assert math.isclose(part.position.y, part_pos_after_move.y)


def test_reset(pos, angle, pos_on_part, pos_on_anchor, offset_angle):
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

    playground.step()

    part_pos_after_move = (pymunk.Vec2d(*random_pos)
                + pymunk.Vec2d(*pos_on_anchor).rotated(random_angle)
                - pymunk.Vec2d(*pos_on_part).rotated(random_angle+offset_angle))

    assert math.isclose(part.position.x, part_pos_after_move.x)
    assert math.isclose(part.position.y, part_pos_after_move.y)

    playground.reset()

    playground.step()

    assert math.isclose(agent.position.x, pos[0], abs_tol=1e-10)
    assert math.isclose(agent.position.y, pos[1], abs_tol=1e-10)


def test_command_and_move(pos, angle, pos_on_part, pos_on_anchor, offset_angle, keep_velocity):
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

    agent.move_to((pos, angle), keep_velocity=keep_velocity)

    for _ in range(100):
        playground.step()

    # After moving, there is still a bit of impulse in the joints
    # Dissipates after a few timesteps

    if not keep_velocity:
        assert math.isclose(agent.position.x, pos[0], abs_tol=1e-4)
        assert math.isclose(agent.position.y, pos[1], abs_tol=1e-4)
        part_pos = (pymunk.Vec2d(*pos)
                + pymunk.Vec2d(*pos_on_anchor).rotated(angle)
                - pymunk.Vec2d(*pos_on_part).rotated(angle+offset_angle))

        assert math.isclose(part.position.x, part_pos.x, abs_tol=1e-4)
        assert math.isclose(part.position.y, part_pos.y, abs_tol=1e-4)

    else:
        assert not math.isclose(agent.position.x, pos[0], abs_tol=1e-4)
        assert not math.isclose(agent.position.y, pos[1], abs_tol=1e-4)
    
    
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

    for _ in range(100):
        playground.step()

    # After moving, there is still a bit of impulse in the joints
    # Dissipates after a few timesteps

    assert math.isclose(agent.position.x, pos[0], abs_tol=1e-4)
    assert math.isclose(agent.position.y, pos[1], abs_tol=1e-4)
    
    part_pos = (pymunk.Vec2d(*pos)
                + pymunk.Vec2d(*pos_on_anchor).rotated(angle)
                - pymunk.Vec2d(*pos_on_part).rotated(angle+offset_angle))

    assert math.isclose(part.position.x, part_pos.x, abs_tol=1e-4)
    assert math.isclose(part.position.y, part_pos.y, abs_tol=1e-4)


def test_agent_reset_sampler():
    playground = EmptyPlayground()
    sampler = FixedCoordinateSampler(position=(0,0), distribution='uniform', contour = Contour(shape='circle', radius=200))

    agent = MockAgent(playground, coordinates=sampler)

    contour = Contour(shape='rectangle', size=(50, 30))
    part = MockAnchoredPart(agent._base,
                            pivot_position_on_part=(10, 10),
                            pivot_position_on_anchor=(10, 10),
                            relative_angle=math.pi/3,
                            rotation_range=math.pi,
                            contour=contour,
                            )

    pos, angle = agent.position, agent.angle

    for _ in range(10):
        playground.reset()

        new_pos, new_angle = agent.position, agent.angle

        assert new_pos != pos
        assert new_angle != angle

        pos, angle != new_pos, new_angle

        part_pos = (pymunk.Vec2d(*new_pos)
                + pymunk.Vec2d(10, 10).rotated(new_angle)
                - pymunk.Vec2d(10, 10).rotated(new_angle+math.pi/3))

        assert math.isclose(part.position.x, part_pos.x, abs_tol=1e-4)
        assert math.isclose(part.position.y, part_pos.y, abs_tol=1e-4)


def test_agent_reset_sampler():
    playground = EmptyPlayground()

    agent = MockAgent(playground)

    contour = Contour(shape='rectangle', size=(50, 30))
    part = MockAnchoredPart(agent._base,
                            pivot_position_on_part=(10, 10),
                            pivot_position_on_anchor=(10, 10),
                            relative_angle=math.pi/3,
                            rotation_range=math.pi,
                            contour=contour,
                            )

    commands = [  (random.uniform(-1, 1), random.uniform(-1, 1), random.uniform(-1, 1)) for _ in range(100) ]

    obj_obj_commands = [{agent: {agent._base.forward_controller: for_vel,
                                 part.joint_controller: joint_rate,
                                 agent._base.angular_vel_controller: ang_vel
                                 }
                         } for for_vel, joint_rate, ang_vel in commands]
    
    str_obj_commands = [{agent.name: {agent._base.forward_controller: for_vel,
                                 part.joint_controller: joint_rate,
                                 agent._base.angular_vel_controller: ang_vel
                                 }
                         } for for_vel, joint_rate, ang_vel in commands]
   
    obj_str_commands = [{agent: {agent._base.forward_controller.name: for_vel,
                                 part.joint_controller.name: joint_rate,
                                 agent._base.angular_vel_controller.name: ang_vel
                                 }
                         } for for_vel, joint_rate, ang_vel in commands]
   
    str_str_commands = [{agent.name: {agent._base.forward_controller.name: for_vel,
                                 part.joint_controller.name: joint_rate,
                                 agent._base.angular_vel_controller.name: ang_vel
                                 }
                         } for for_vel, joint_rate, ang_vel in commands]
   

    obj_np = [{agent: np.asarray([for_vel, ang_vel, joint_rate])} for for_vel, joint_rate, ang_vel in commands]
   
    for command in obj_obj_commands:
        playground.step(command)

    final_position = agent.position

    for command_input in [str_obj_commands, obj_str_commands, str_str_commands, obj_np]:

        playground.reset()

        for command in command_input:
            playground.step(command)

        assert math.isclose(agent.position.x, final_position.x, abs_tol=1e-9)
        assert math.isclose(agent.position.y, final_position.y, abs_tol=1e-9)

