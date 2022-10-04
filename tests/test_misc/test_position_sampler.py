import pytest

from spg.playground import Playground
from spg.utils.position import GaussianCoordinateSampler, UniformCoordinateSampler


@pytest.fixture(scope="module", params=[10, 20])
def radius(request):
    return request.param


@pytest.fixture(scope="module", params=[10, 20])
def width(request):
    return request.param


@pytest.fixture(scope="module", params=[15, 25])
def height(request):
    return request.param


@pytest.fixture(scope="module", params=[5, 10])
def sigma(request):
    return request.param


@pytest.fixture(scope="module", params=[(100, 100), (200, -100)])
def center(request):
    return request.param


def test_uniform_radius(radius, center):
    pg = Playground()

    sampler = UniformCoordinateSampler(pg, center=center, radius=radius)

    for coord in sampler.sample():
        (x, y), _ = coord
        assert (x - center[0]) ** 2 + (y - center[1]) ** 2 <= radius**2


def test_uniform_width(width, center):
    pg = Playground()

    sampler = UniformCoordinateSampler(pg, center=center, width=width)

    for coord in sampler.sample():
        (x, y), _ = coord
        assert (x - center[0]) ** 2 <= (width / 2) ** 2
        assert (y - center[1]) ** 2 <= (width / 2) ** 2


def test_uniform_width_height(width, height, center):
    pg = Playground()

    sampler = UniformCoordinateSampler(pg, center=center, width=width, height=height)

    for coord in sampler.sample():
        (x, y), _ = coord
        assert (x - center[0]) ** 2 <= (width / 2) ** 2
        assert (y - center[1]) ** 2 <= (height / 2) ** 2


def test_gaussian_radius(radius, center, sigma):
    pg = Playground()

    sampler = GaussianCoordinateSampler(pg, sigma, center=center, radius=radius)

    count_in = 0
    count_out = 0

    for coord in sampler.sample():
        (x, y), _ = coord
        assert (x - center[0]) ** 2 + (y - center[1]) ** 2 <= radius**2

        if (x - center[0]) ** 2 + (y - center[1]) ** 2 <= radius**2 / 2:
            count_in += 1
        else:
            count_out += 1

    assert count_in > count_out


def test_gaussian_width(width, center, sigma):
    pg = Playground()

    sampler = GaussianCoordinateSampler(pg, sigma, center=center, width=width)

    count_in = 0
    count_out = 0

    for coord in sampler.sample():
        (x, y), _ = coord
        assert (x - center[0]) ** 2 <= (width / 2) ** 2
        assert (y - center[1]) ** 2 <= (width / 2) ** 2

        if (x - center[0]) ** 2 <= (width / 2) ** 2 and (y - center[1]) ** 2 <= (
            width / 2
        ) ** 2 / 2:
            count_in += 1
        else:
            count_out += 1

    assert count_in > count_out


def test_gaussian_width_height(width, height, center, sigma):
    pg = Playground()

    sampler = GaussianCoordinateSampler(
        pg, sigma, center=center, width=width, height=height
    )

    count_in = 0
    count_out = 0

    for coord in sampler.sample():
        (x, y), _ = coord
        assert (x - center[0]) ** 2 <= (width / 2) ** 4
        assert (y - center[1]) ** 2 <= (height / 2) ** 4

        if (x - center[0]) ** 2 <= (width / 2) ** 2 and (y - center[1]) ** 2 <= (
            height / 2
        ) ** 2 / 2:
            count_in += 1
        else:
            count_out += 1

    assert count_in > count_out
