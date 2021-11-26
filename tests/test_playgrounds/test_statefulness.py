from typing import Optional

import numpy as np
import pytest

from simple_playgrounds.playground.playground import EmptyPlayground
from simple_playgrounds.common.contour import Contour
from simple_playgrounds.common.position_utils import FixedCoordinateSampler
from ..mock_entities import MockPhysical


@pytest.fixture(scope="module", params=[1, 10, 42])
def seed(request):
    return request.param

@pytest.fixture(scope="module", params=[1, 39, 40, 41, 100])
def ts_rewind(request):
    return request.param

@pytest.fixture(scope="module", params=[1, 10, 50])
def ts_checkpoint(request):
    return request.param


def test_set_seed(seed):

    contour = Contour(shape='circle', radius=10)

    end_positions = []

    for i in range(3):

        playground = EmptyPlayground(seed=seed)

        contour_sampler = Contour(shape='rectangle', size=(100, 100))
        sampler = FixedCoordinateSampler(position=(0, 0), distribution='uniform', contour=contour_sampler)

        for _ in range(20):
            ent = MockPhysical(contour=contour, traversable=True, movable=True, mass=5)
            playground.add(ent, sampler)
            ent._pm_body.apply_impulse_at_local_point( playground.rng.uniform(-10, 10, 2).tolist())

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
    end_positions = []

    playground = EmptyPlayground(checkpoints=ts_checkpoint)

    contour_sampler = Contour(shape='rectangle', size=(100, 100))
    sampler = FixedCoordinateSampler(position=(0, 0), distribution='uniform', contour=contour_sampler)

    for _ in range(10):
        ent = MockPhysical(contour=contour, traversable=True, movable=True, mass=5)
        playground.add(ent, sampler)
        ent._pm_body.apply_impulse_at_local_point(playground.rng.uniform(-10, 10, 2).tolist())

    # First run
    for i in range(100):
        playground.step()
    end_pos = np.asarray([ent.position for ent in playground._physical_entities])
    end_positions.append(end_pos)

    # Rewind from start
    playground.rewind()
    for i in range(100):
        playground.step()
    end_pos = np.asarray([ent.position for ent in playground._physical_entities])
    end_positions.append(end_pos)

    # Rewind from timestep
    playground.rewind(timestep=ts_rewind)
    for i in range(100-ts_rewind)
    vels_2 = np.asarray([ent.velocity for ent in playground._physical_entities])


    assert np.all(vels - vels_2 != 0)

    for end_pos in end_positions:
        assert np.all(end_pos == end_positions[0])


def goto