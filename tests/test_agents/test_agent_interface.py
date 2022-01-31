import pytest
from simple_playgrounds.agent.controller import ContinuousController, DiscreteController, RangeController

import numpy as np
from simple_playgrounds.playground.playground import EmptyPlayground
from tests.mock_agents import MockAgent, MockBase
from tests.mock_entities import MockBarrier, MockPhysical
from simple_playgrounds.entity.embodied.contour import Contour


def test_agent_in_playground():

    playground = EmptyPlayground()
    agent = MockAgent(playground)
    
    assert agent in playground.agents
    assert playground.entities == []
    assert agent._base in playground._shapes_to_entities.values()
    assert agent._base in agent.parts
    
    for part in agent.parts:
        assert part in playground._shapes_to_entities.values()
        assert part.agent == agent

    agent.remove(definitive=False)
    
    assert agent not in playground.agents
    assert not playground.space.shapes
    assert playground._shapes_to_entities != {}

    playground.reset()
    
    assert agent in playground.agents
    
    agent.remove(definitive=True)
    
    assert agent not in playground.agents
    assert not playground.space.shapes
    assert playground._shapes_to_entities == {}

    playground.reset()
    
    assert agent not in playground.agents



@pytest.fixture(scope='module', params=[1, 5])
def range_controller(request):
    return request.param


def test_range_controller(range_controller):

    playground = EmptyPlayground()
    agent = MockAgent(playground)
    controller = RangeController(part=agent._base, n=range_controller)

    for _ in range(200):
        assert controller.sample() in list(range(range_controller))

    controller.set_command(command=controller.sample())

    with pytest.raises(ValueError):
        controller.set_command(range_controller, hard_check=True)


@pytest.fixture(scope='module', params = [-2.12, 1.4, 0, 1.5, 2.43]) 
def min_controller(request):
    return request.param


@pytest.fixture(scope='module', params = [-2.42, 1.5, 0, 1.3, 2.83]) 
def max_controller(request):
    return request.param


def test_cont_controller(min_controller, max_controller):
    
    playground = EmptyPlayground()
    agent = MockAgent(playground)
    
    if min_controller > max_controller:
        with pytest.raises(ValueError):
            ContinuousController(min_controller, max_controller, part=agent._base)

    else:

        controller = ContinuousController(min_controller, max_controller, part=agent._base)

        with pytest.raises(ValueError):
            controller.set_command(min_controller-0.1, hard_check=True)

        with pytest.raises(ValueError):
            controller.set_command(max_controller+0.1, hard_check=True)


def test_controller_forward():
    
    playground = EmptyPlayground()
    agent = MockAgent(playground)

    commands = {agent: {agent._base.forward_controller: 1}}
    
    assert agent.position == (0, 0)

    playground.step(commands=commands)

    assert agent.position != (0, 0)
    assert agent.position.x > 0
    assert agent.position.y == 0


def test_controller_rotate():
    
    playground = EmptyPlayground()
    agent = MockAgent(playground)

    commands = {agent: {agent._base.angular_vel_controller: 1}}
    
    assert agent.position == (0, 0)
    assert agent.angle == 0

    playground.step(commands=commands)

    assert agent.position == (0, 0)
    assert agent.angle > 0


def test_command_interface():

    playground = EmptyPlayground()
    agent = MockAgent(playground)

    agent_identifier = [agent, agent.name]
    controller_identifier = [agent._base.forward_controller,
                             agent._base.forward_controller.name]

    for ag_id in agent_identifier:
        for cont_id in controller_identifier:
            commands = {ag_id: {cont_id: 1}}
            playground.step(commands=commands)






# def test_agent_initial_position():

#     agent = MockAgent()
#     playground = EmptyPlayground()
    
#     playground.add(agent)

#     assert agent.position == (0, 0)
#     assert agent.angle == 0


# def test_agent_forward_movable():
 
#     agent = MockAgent()
#     playground = EmptyPlayground()
    
#     playground.add(agent)

#     contour = Contour(shape='circle', radius=10)
#     obstacle = MockPhysical(**contour.dict_attributes, movable=True, mass=5, initial_coordinates=((0,0), 0)
#     playground.add(obstacle, ((50, 0), 0))

#     actions = {}
#     for controller in agent.controllers:
#         actions[controller] = controller.max


# def test_agent_forward_obstacle():
#     pass


# def test_agent_control():
#     pass


# def test_seed():
#     pass


# def run_engine(base_agent, pg_class, **pg_params):
#     playground = pg_class(**pg_params)
#     playground.add_agent(base_agent, allow_overlapping=False)

#     engine = Engine(playground, time_limit=1000)
#     engine.run()

#     assert 0 < base_agent.position[0] < playground.size[0]
#     assert 0 < base_agent.position[1] < playground.size[1]

#     playground.remove_agent(base_agent)


# def test_agents_in_empty_room(is_interactive, going_backward, moving_laterally,
#                               all_agent_cls, random_controller):

#     agent = all_agent_cls(
#         controller=random_controller(),
#         interactive=is_interactive,
#         backward=going_backward,
#         lateral=moving_laterally,
#     )

#     run_engine(agent, SingleRoom, size=(300, 300))


# @pytest.mark.parametrize(
#     "pg,limits",
#     [(SingleRoom((300, 300)), (300, 300)),
#      (GridRooms((400, 400), (2, 2), doorstep_size=60), (200, 200))],
# )
# def test_agent_initial_position(base_forward_agent_random, pg, limits):

#     # When position is not set
#     agent = base_forward_agent_random
#     pg.add_agent(agent)
#     assert 0 < agent.position[0] < limits[0]
#     assert 0 < agent.position[1] < limits[1]
#     pg.remove_agent(agent)

#     # When position is fixed
#     pg.add_agent(agent, ((50, 50), 0))
#     assert agent.position == (50, 50)
#     pg.remove_agent(agent)

#     # When position is from area of room
#     position_sampler = pg.grid_rooms[0][0].get_area_sampler()
#     pg.add_agent(agent, position_sampler)
#     assert 0 < agent.position[0] < limits[0]
#     assert 0 < agent.position[1] < limits[1]


# def test_agent_overlapping(base_forward_agent_random, empty_playground):

#     elem = Physical(config_key='square')
#     empty_playground.add_element(elem, ((50, 50), 0))
#     empty_playground.add_agent(base_forward_agent_random, ((50, 50), 0))

#     assert empty_playground._overlaps(base_forward_agent_random)
#     assert empty_playground._overlaps(base_forward_agent_random, elem)

#     empty_playground.remove_agent(base_forward_agent_random)

#     with pytest.raises(ValueError):
#         empty_playground.add_agent(base_forward_agent_random, ((50, 50), 0),
#                                    allow_overlapping=False)

#     with pytest.raises(ValueError):
#         empty_playground.add_agent(base_forward_agent_random)
#         empty_playground.add_agent(base_forward_agent_random)
