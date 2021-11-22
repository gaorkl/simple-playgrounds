import pytest

from simple_playgrounds.playground.playground import EmptyPlayground
from simple_playgrounds.common.contour import Contour


def test_circle_contour():

    contour = Contour(shape='circle', radius=10)
    mask = contour.mask

    assert mask[10, 10] == 1
    assert mask[2, 2] == 0


def test_rectangle_contour():

    contour = Contour(shape='rectangle', size=(10, 3))
    mask = contour.mask

    assert mask.shape == (11, 11)
    assert mask[3, 5] == 0