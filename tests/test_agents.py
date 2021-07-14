import pytest

from simple_playgrounds.engine import Engine
from simple_playgrounds.playgrounds.layouts import GridRooms, SingleRoom
from simple_playgrounds.common.position_utils import CoordinateSampler


def run_engine(base_agent, pg_class, **pg_params):
    playground = pg_class(**pg_params)
    playground.add_agent(base_agent, allow_overlapping=False)

    engine = Engine(playground, time_limit=100)
    engine.run()

    assert 0 < base_agent.position[0] < playground.size[0]
    assert 0 < base_agent.position[1] < playground.size[1]

    playground.remove_agent(base_agent)


def test_agents_in_empty_room(is_interactive, going_backward, moving_laterally, pg_cls,
                              all_agent_cls, random_controller):

    agent = all_agent_cls(
        controller=random_controller(),
        interactive=is_interactive,
        backward=going_backward,
        lateral=moving_laterally,
    )

    run_engine(agent, SingleRoom, size = (300,300))


@pytest.mark.parametrize(
    "pg,limits",
    [(SingleRoom((300, 300)), (300, 300)),
     (GridRooms((400, 400), (2, 2), doorstep_size=60), (200, 200))],
)
def test_agent_initial_position1(base_forward_agent, pg, limits):
    agent = base_forward_agent
    pg.add_agent(agent)

    assert 0 < agent.position[0] < limits[0]
    assert 0 < agent.position[1] < limits[1]


def test_agent_initial_position2(base_forward_agent):
    agent = base_forward_agent
    # Modifying initial position in playground
    playground = SingleRoom((300, 300))
    playground.initial_agent_coordinates = ((50, 50), 0)
    playground.add_agent(agent)
    assert agent.position == (50, 50)
    playground.remove_agent(agent)


def test_agent_initial_position3(base_forward_agent):
    agent = base_forward_agent
    # Setting initial position in playground as PositionAreaSampler
    playground = SingleRoom((300, 300))
    first_room = playground.grid_rooms[0][0]
    center, shape = first_room.center, first_room.size
    playground.initial_agent_coordinates = CoordinateSampler(
        center, area_shape='rectangle', size=shape)
    playground.add_agent(agent)
    pos_1 = agent.position
    playground.remove_agent(agent)
    playground.add_agent(agent)
    assert agent.position != pos_1
    playground.remove_agent(agent)
