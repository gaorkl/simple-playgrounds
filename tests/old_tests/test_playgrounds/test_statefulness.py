from typing import Optional

import numpy as np
import pytest

from simple_playgrounds.playground.playground import EmptyPlayground
from simple_playgrounds.common.contour import Contour
from simple_playgrounds.common.position_utils import FixedCoordinateSampler
from ..mock_entities import MockPhysical

TOTAL_TS = 100


@pytest.fixture(scope="module", params=[1, 10, 42])
def seed(request):
    return request.param


@pytest.fixture(scope="module", params=[1, 39, 40, 41, 80])
def ts_rewind(request):
    return request.param


@pytest.fixture(scope="module", params=[10, 50])
def ts_checkpoint(request):
    return request.param


def apply_random_impulse(playground):
    for ent in playground._physical_entities:
        ent._pm_body.apply_impulse_at_local_point(playground.rng.uniform(-10, 10, 2).tolist())


def test_set_seed(seed):

    contour = Contour(shape='circle', radius=10)

    end_positions = []

    for i in range(3):

        playground = EmptyPlayground(seed=seed)

        contour_sampler = Contour(shape='rectangle', size=(100, 100))
        sampler = FixedCoordinateSampler(position=(0, 0), distribution='uniform', contour=contour_sampler)

        for _ in range(20):
            ent = MockPhysical(contour=contour, traversable=True, movable=True, mass=5, initial_coordinates=((0,0), 0)
            playground.add(ent, sampler)

        playground.reset()

        apply_random_impulse(playground)

        vels = np.asarray([ent.velocity for ent in playground._physical_entities])

        for i in range(10):
            playground.step()

        vels_2 = np.asarray([ent.velocity for ent in playground._physical_entities])
        end_pos = np.asarray([ent.position for ent in playground._physical_entities])

        end_positions.append(end_pos)

        assert np.all(vels-vels_2 != 0)

    for end_pos in end_positions:
        assert np.all(end_pos == end_positions[0])


def test_rewind(ts_rewind, ts_checkpoint):

    contour = Contour(shape='circle', radius=10)

    playground = EmptyPlayground()

    contour_sampler = Contour(shape='rectangle', size=(100, 100))
    sampler = FixedCoordinateSampler(position=(0, 0), distribution='uniform', contour=contour_sampler)

    for _ in range(10):
        ent = MockPhysical(contour=contour, traversable=True, movable=True, mass=5, initial_coordinates=((0,0), 0)
        playground.add(ent, sampler)

    apply_random_impulse(playground)
    playground.save_checkpoint()

    for ts in range(TOTAL_TS):
        playground.step()

        if (playground.timestep+1) % ts_checkpoint == 0:
            playground.save_checkpoint()

    end_pos = np.asarray([ent.position for ent in playground._physical_entities])
    end_ts = playground.timestep

    playground.rewind(ts_rewind)

    for i in range(ts_rewind):
        playground.step()

    end_ts_rewind = playground.timestep
    assert end_ts_rewind == end_ts

    end_pos_rewind = np.asarray([ent.position for ent in playground._physical_entities])
    assert np.all(end_pos == end_pos_rewind)


def test_rewind_alternate(ts_rewind, ts_checkpoint):

    contour = Contour(shape='circle', radius=10)

    playground = EmptyPlayground()

    contour_sampler = Contour(shape='rectangle', size=(100, 100))
    sampler = FixedCoordinateSampler(position=(0, 0), distribution='uniform', contour=contour_sampler)

    for _ in range(10):
        ent = MockPhysical(contour=contour, traversable=True, movable=True, mass=5, initial_coordinates=((0,0), 0)
        playground.add(ent, sampler)

    # Apply random perturbation and go to end

    apply_random_impulse(playground)
    playground.save_checkpoint()

    for ts in range(TOTAL_TS):
        playground.step()

        if (playground.timestep+1) % ts_checkpoint == 0:
            playground.save_checkpoint()

    # rewind, apply other perturbation, and go to the end
    playground.rewind(ts_rewind)
    apply_random_impulse(playground)

    for i in range(ts_rewind):
        playground.step()

    end_pos_rewind_1 = np.asarray([ent.position for ent in playground._physical_entities])

    playground.rewind(ts_rewind)
    apply_random_impulse(playground)

    for i in range(ts_rewind):
        playground.step()

    end_pos_rewind_2 = np.asarray([ent.position for ent in playground._physical_entities])

    playground.rewind(ts_rewind, random_alternate=True)
    apply_random_impulse(playground)

    for i in range(ts_rewind):
        playground.step()

    end_pos_rewind_3 = np.asarray([ent.position for ent in playground._physical_entities])

    assert np.all(end_pos_rewind_1 == end_pos_rewind_2)
    assert np.all(end_pos_rewind_2 != end_pos_rewind_3)



