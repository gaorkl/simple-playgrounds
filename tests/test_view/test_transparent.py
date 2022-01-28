import random
import math

import pytest

import numpy as np
from matplotlib.colors import to_rgb
from skimage import transform
from simple_playgrounds.common import view

from simple_playgrounds.playground.playground import EmptyPlayground
from simple_playgrounds.common.view import AnchoredView, FixedGlobalView
from simple_playgrounds.entity.embodied.contour import Contour

from ..mock_entities import MockHaloTrigger, MockPhysical, MockZoneTrigger

center_coord = (0, 0), 0


def test_transparent():

    playground = EmptyPlayground()
    view_global = FixedGlobalView(playground, center_coord, size_on_playground=(100,100))
    view_global_transparent = FixedGlobalView(playground, center_coord, size_on_playground=(100,100), draw_transparent=True)

    view_empty = view_global.update_view()

    contour = Contour(shape='circle', radius=10)
    ent_1 = MockPhysical(playground, center_coord, contour=contour, transparent=True, movable=True, mass=5)

    view_transparent = view_global_transparent.update_view()
    view_no_transparent = view_global.update_view()

    assert np.all(view_empty == view_no_transparent)
    assert np.any(view_empty != view_transparent)
    # Assert that pixels drawn are the same, but different colors
    non_zero_transparent = view_transparent != (0,0,0)

    ent_1.remove()

    ent_2 = MockPhysical(playground, center_coord, contour=contour, transparent=False, movable=True, mass=5)
    
    view_visible_entity = view_global.update_view()
    
    non_zero_visible = view_visible_entity != (0,0,0)

    assert np.all(non_zero_transparent == non_zero_visible)
    assert np.all(view_transparent[np.where(non_zero_transparent)] != view_visible_entity[np.where(non_zero_visible)]  )

def test_interactive():

    playground = EmptyPlayground()
    view_global = FixedGlobalView(playground, center_coord, size_on_playground=(100,100))

    view_global_interactive = FixedGlobalView(playground, center_coord, size_on_playground=(100,100), draw_interaction=True)

    contour = Contour(shape='circle', radius=10)
    ent_1 = MockZoneTrigger(playground, center_coord, contour=contour)

    view_transparent = view_global_interactive.update_view()
    view_no_transparent = view_global.update_view()
    assert np.any(view_no_transparent != view_transparent)

