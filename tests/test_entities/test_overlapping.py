import pytest

from simple_playgrounds.playground.playground import EmptyPlayground
from tests.mock_entities import MockPhysical, MockZoneTrigger
from simple_playgrounds.common.contour import Contour
from simple_playgrounds.common.position_utils import CoordinateSampler


def test_overlap_fixed():

    playground = EmptyPlayground()

    # Two fixed entities can be superimposed (Background)

    contour = Contour('circle', 10, None, None)
    ent_1 = MockPhysical(**contour._asdict())
    playground.add(ent_1, ((0, 0), 0))

    ent_2 = MockPhysical(**contour._asdict())
    playground.add(ent_2, ((0, 1), 0))


def test_overlap_movable():

    playground = EmptyPlayground()

    # If overlapping is prohibited, then placing an entity on top of a physical entity should raise an error.

    contour = Contour('circle', 10, None, None)
    ent_1 = MockPhysical(**contour._asdict())
    playground.add(ent_1, ((0, 0), 0))

    ent_2 = MockPhysical(**contour._asdict())
    playground.add(ent_2, ((0, 1), 0))

    ent_3 = MockPhysical(**contour._asdict())
    with pytest.raises(ValueError):
        playground.add(ent_3, ((0, 1), 0), allow_overlapping=False)


def test_overlap_interactive():

    playground = EmptyPlayground()

    # Placing a physical on an interactive (zone) is possible

    contour = Contour('circle', 10, None, None)
    ent_1 = MockZoneTrigger(**contour._asdict(), texture=(10, 10, 10))
    playground.add(ent_1, ((0, 1), 0))

    ent_2 = MockPhysical(**contour._asdict())
    playground.add(ent_2, ((0, 0), 0), allow_overlapping=False)


def test_overlaps_physical():

    playground = EmptyPlayground()

    # Placing a physical on an interactive (zone) is possible

    contour = Contour('circle', 10, None, None)
    ent_1 = MockPhysical(**contour._asdict())
    playground.add(ent_1, ((0, 1), 0))

    ent_2 = MockPhysical(**contour._asdict())
    with pytest.raises(ValueError):
        playground.add(ent_2, ((0, 0), 0), allow_overlapping=False)


def test_overlaps_coordinate_sampler():

    playground = EmptyPlayground()

    # Placing a physical on an interactive (zone) is possible

    contour = Contour('circle', 10, None, None)
    ent_1 = MockPhysical(**contour._asdict())
    playground.add(ent_1, ((0, 1), 0))

    coord_sampler = CoordinateSampler(center=(0, 0), size=(100, 100), area_shape='rectangle')
    coord_sampler.sample()

    ent_2 = MockPhysical(**contour._asdict())
    playground.add(ent_2, coord_sampler, allow_overlapping=False)




