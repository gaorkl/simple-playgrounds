import pymunk

from simple_playgrounds.common.contour import Contour
from simple_playgrounds.common.position_utils import FixedCoordinateSampler, AnchoredCoordinateSampler
from simple_playgrounds.playground.playground import EmptyPlayground
from tests.mock_entities import MockPhysical


def test_circular_uniform_sampler(radius):

    center = (-radius, 3*radius)
    contour = Contour(shape='circle', radius=radius)
    sampler = FixedCoordinateSampler(position=center, distribution='uniform', contour=contour)

    for pos, angle in sampler.sample():
        pos = pymunk.Vec2d(*pos)
        assert pos.get_distance(center) <= radius


def test_circular_gaussian_sampler(radius):

    center = (-radius, 3*radius)
    contour = Contour(shape='circle', radius=radius)
    sampler = FixedCoordinateSampler(position=center, distribution='gaussian', sigma=5, contour=contour)

    for pos, angle in sampler.sample():
        pos = pymunk.Vec2d(*pos)
        assert pos.get_distance(center) <= radius


def test_rectangular_uniform_sampler(radius):

    width = radius
    length = 2*radius
    center = (-radius, 4*radius)

    contour = Contour(shape='rectangle', size=(width, length))

    sampler = FixedCoordinateSampler(position=center, distribution='uniform', contour=contour)

    for (x, y), angle in sampler.sample():
        assert center[0] - width/2 <= x <= center[0] + width/2
        assert center[1] - length/2 <= y <= center[1] + length/2


def test_anchor_sampler(radius):

    width = radius
    length = 2 * radius
    center = (-radius, 4 * radius)

    playground = EmptyPlayground()

    # Two traversable shouldn't collide with either traversables or non-traversables

    contour_ent = Contour(shape='circle', radius=4)
    ent_1 = MockPhysical(contour=contour_ent)
    playground.add(ent_1, (center, 0))

    contour_sampler = Contour(shape='rectangle', size=(width, length))
    sampler = AnchoredCoordinateSampler(anchor=ent_1, distribution='uniform', contour=contour_sampler)

    for (x, y), angle in sampler.sample():
        assert center[0] - width / 2 <= x <= center[0] + width / 2
        assert center[1] - length / 2 <= y <= center[1] + length / 2

    new_center = (3*radius, -4*radius)
    ent_1.move_to((new_center, 0))

    for (x, y), angle in sampler.sample():
        assert new_center[0] - width / 2 <= x <= new_center[0] + width / 2
        assert new_center[1] - length / 2 <= y <= new_center[1] + length / 2
