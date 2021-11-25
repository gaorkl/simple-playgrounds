import pytest

from simple_playgrounds.playground.playground import EmptyPlayground
from tests.mock_entities import MockPhysical, MockZoneTrigger
from simple_playgrounds.common.contour import Contour
from simple_playgrounds.common.position_utils import FixedCoordinateSampler


def test_overlap_fixed():

    playground = EmptyPlayground()

    # Two fixed entities can be superimposed (Background)

    contour = Contour(shape='circle', radius=10)
    ent_1 = MockPhysical(contour=contour)
    playground.add(ent_1, ((0, 0), 0))

    ent_2 = MockPhysical(contour=contour)
    playground.add(ent_2, ((0, 1), 0))


def test_overlap_movable():

    playground = EmptyPlayground()

    # If overlapping is prohibited, then placing an entity on top of a physical entity should raise an error.

    contour = Contour(shape='circle', radius=10)
    ent_1 = MockPhysical(contour=contour)
    playground.add(ent_1, ((0, 0), 0))

    ent_2 = MockPhysical(contour=contour)
    playground.add(ent_2, ((0, 1), 0))

    ent_3 = MockPhysical(contour=contour)
    with pytest.raises(ValueError):
        playground.add(ent_3, ((0, 1), 0), allow_overlapping=False)


def test_overlap_interactive():

    playground = EmptyPlayground()

    # Placing a physical on an interactive (zone) is possible

    contour = Contour(shape='circle', radius=10)
    ent_1 = MockZoneTrigger(contour=contour, texture=(10, 10, 10))
    playground.add(ent_1, ((0, 1), 0))

    ent_2 = MockPhysical(contour=contour)
    playground.add(ent_2, ((0, 0), 0), allow_overlapping=False)


def test_overlaps_physical():

    playground = EmptyPlayground()

    # Placing a physical on an interactive (zone) is possible

    contour = Contour(shape='circle', radius=10)
    ent_1 = MockPhysical(contour=contour)
    playground.add(ent_1, ((0, 1), 0))

    ent_2 = MockPhysical(contour=contour)
    with pytest.raises(ValueError):
        playground.add(ent_2, ((0, 0), 0), allow_overlapping=False)


def test_overlaps_coordinate_sampler():

    playground = EmptyPlayground()

    # Placing a physical on an interactive (zone) is possible

    contour = Contour(shape='circle', radius=10)
    ent_1 = MockPhysical(contour=contour)
    playground.add(ent_1, ((0, 1), 0))

    contour_sampler = Contour(shape='rectangle', size=(30, 30))
    coord_sampler = FixedCoordinateSampler(position=(0, 0), contour=contour_sampler, distribution='uniform')

    ent_2 = MockPhysical(contour=contour)
    playground.add(ent_2, coord_sampler, allow_overlapping=False)

    assert ent_1._pm_shape.shapes_collide(ent_2._pm_shape)


def test_overlaps_coordinate_sampler_many():

    playground = EmptyPlayground()

    # Placing a physical on an interactive (zone) is possible

    contour_entity = Contour(shape='circle', radius=5)

    contour_sampler = Contour(shape='rectangle', size=(40, 40))
    coord_sampler = FixedCoordinateSampler(position=(0, 0), contour=contour_sampler, distribution='uniform')

    # We can add many entities until we can't
    with pytest.raises(ValueError):
        for i in range(100):
            ent = MockPhysical(contour=contour_entity)
            playground.add(ent, coord_sampler, allow_overlapping=False)

