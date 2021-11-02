import pytest

from simple_playgrounds.agent.agents import HeadAgent
from simple_playgrounds.agent.controllers import RandomContinuous
from simple_playgrounds.element.elements.contact import Candy
from simple_playgrounds.common.spawner import Spawner
from simple_playgrounds.engine import Engine
from simple_playgrounds.playground.layouts import SingleRoom


@pytest.mark.parametrize(
    "entity_counter,entity_type,entity_params",
    (
        ("elements", Candy, {}),
        ("agents", HeadAgent, {"controller": RandomContinuous()}),
    ),
)
def test_spawner(spawner_limits, entity_counter, entity_type, entity_params):
    playground = SingleRoom(size=(200, 200))

    max_elem, prod_limit = spawner_limits
    max_in_pg = min(spawner_limits)

    spawner = Spawner(
        entity_type,
        playground.grid_rooms[0][0].get_area_sampler(),
        entity_produced_params=entity_params,
        probability=1,
        max_elements_in_playground=max_in_pg,
        production_limit=prod_limit,
    )
    playground.add_spawner(spawner)

    engine = Engine(playground, time_limit=100)

    while engine.game_on:
        engine.step()

    count = len(
        [
            elem
            for elem in getattr(playground, entity_counter)
            if isinstance(elem, entity_type)
        ]
    )

    assert count == max_in_pg
