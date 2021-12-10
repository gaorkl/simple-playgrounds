import random
import math

import pytest

import numpy as np
from matplotlib.colors import to_rgb
from skimage import transform
from simple_playgrounds.common import view

from simple_playgrounds.playground.playground import EmptyPlayground
from simple_playgrounds.common.view import AnchoredView, FixedGlobalView
from simple_playgrounds.common.contour import Contour

from ..mock_entities import MockPhysical


def test_transparent(shape, position, angle, radius, size_on_pg):
    """ Rotating elements by the correct angle should lead to the same image """

    playground = EmptyPlayground()
    view_global = FixedGlobalView(playground=playground, size_on_playground=size_on_pg,
                                 coordinates=((0, 0), 0))

    view_empty = view_global.update_view()
    
    contour = Contour(shape=shape, radius=radius)
    ent_1 = MockPhysical(contour=contour, transparent=True, movable=True, mass=5)

    playground.add(ent_1, (position, angle))

    view_draw_invisible = view_global.update_view(draw_invisible=True)
    view_not_draw_invisible = view_global.update_view()
    
    assert np.all(view_empty == view_not_draw_invisible)
    assert np.all(view_empty != view_draw_invisible)
    
