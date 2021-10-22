from simple_playgrounds.engine import Engine
from simple_playgrounds.playgrounds.layouts import SingleRoom

from simple_playgrounds.elements.spawner import Spawner
from simple_playgrounds.elements.collection.contact import Candy


def test_spawner(spawner_limits):
    playground = SingleRoom(size=(200, 200))

    max_elem, prod_limit = spawner_limits
    max_in_pg = min(spawner_limits)

    spawner = Spawner(Candy, playground.grid_rooms[0][0].get_area_sampler(), probability=1,
                  max_elements_in_playground=max_in_pg,
                  production_limit=prod_limit)
    playground.add_spawner(spawner)

    engine = Engine(playground, time_limit=100)

    while engine.game_on:
        engine.step()

    count = len([elem for elem in playground.elements if isinstance(elem, Candy)])

    assert count == max_in_pg
