import pytest

from simple_playgrounds import Engine
from simple_playgrounds.agents.parts.controllers import Random
from simple_playgrounds.playgrounds.empty import ConnectedRooms2D, SingleRoom
from simple_playgrounds.utils.position_utils import CoordinateSampler


def run_engine(agent, pg_class):
    playground = pg_class()
    playground.add_agent(agent)

    engine = Engine(playground, time_limit=1000)
    engine.run()

    assert 0 < agent.position[0] < playground.size[0]
    assert 0 < agent.position[1] < playground.size[1]

    playground.remove_agent(agent)


def test_base_agent(is_interactive, platform_cls, pg_cls, agent_cls):
    agent = agent_cls(controller=Random(),
                      interactive=is_interactive,
                      platform=platform_cls)

    run_engine(agent, pg_cls)


@pytest.mark.parametrize(
    "pg,limits",
    [(SingleRoom((300, 300)), (300, 300)),
     (ConnectedRooms2D((400, 400), (2, 2)), (200, 200))],
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
    center, shape = playground.area_rooms[(0, 0)]
    playground.initial_agent_coordinates = CoordinateSampler(
        center, area_shape='rectangle', width_length=shape)
    playground.add_agent(agent)
    pos_1 = agent.position
    playground.remove_agent(agent)
    playground.add_agent(agent)
    assert agent.position != pos_1
    playground.remove_agent(agent)
