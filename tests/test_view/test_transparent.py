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


def test_transparent():

    playground = EmptyPlayground()
    view_global = FixedGlobalView(playground=playground, size_on_playground=(100,100),
                                 coordinates=((0, 0), 0))

    view_global_transparent = FixedGlobalView(playground=playground, size_on_playground=(100,100),
                                 coordinates=((0, 0), 0), draw_transparent = True)

    view_empty = view_global.update_view()
    
    contour = Contour(shape='circle', radius=10)
    ent_1 = MockPhysical(contour=contour, transparent=True, movable=True, mass=5, initial_coordinates=((0,0), 0)

    playground.add(ent_1, ((0,0), 0))

    view_transparent = view_global_transparent.update_view()
    view_no_transparent = view_global.update_view()
    
    assert np.all(view_empty == view_no_transparent)
    assert np.any(view_empty != view_transparent)
    # Assert that pixels drawn are the same, but different colors
    non_zero_transparent = view_transparent != (0,0,0)

    playground.remove(ent_1)

    ent_2 = MockPhysical(contour=contour, transparent=False, movable=True, mass=5, initial_coordinates=((0,0), 0)
    playground.add(ent_2, ((0,0), 0))
    
    view_visible_entity = view_global.update_view()
    
    non_zero_visible = view_visible_entity != (0,0,0)

    assert np.all(non_zero_transparent == non_zero_visible)
    assert np.all(view_transparent[np.where(non_zero_transparent)] != view_visible_entity[np.where(non_zero_visible)]  )

def test_interactive():

    playground = EmptyPlayground()
    view_global = FixedGlobalView(playground=playground, size_on_playground=(100,100),
                                 coordinates=((0, 0), 0))

    view_global_interactive = FixedGlobalView(playground=playground, size_on_playground=(100,100),
                                 coordinates=((0, 0), 0), draw_interaction=True)

    contour = Contour(shape='circle', radius=10)
    ent_1 = MockZoneTrigger(contour=contour)

    playground.add(ent_1, ((0,0), 0))

    view_transparent = view_global_interactive.update_view()
    view_no_transparent = view_global.update_view()
    assert np.any(view_no_transparent != view_transparent)

