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


def test_anchored(shape, position, angle, radius, size_on_pg):

    playground = EmptyPlayground()
    contour = Contour(shape=shape, radius=radius)
    ent_1 = MockPhysical(contour=contour, movable=True, mass=5)

    playground.add(ent_1, (position, angle))

    view_anchored = AnchoredView(anchor=ent_1, size_on_playground=size_on_pg).update_view()

    view_global = FixedGlobalView(playground=playground, size_on_playground=size_on_pg,
                           coordinates=((0, 0), 0)).update_view()

    if ent_1.position == (0,0) and (ent_1.angle == 0 or shape=='circle'): 
        assert np.all(view_global == view_anchored)

    else:
        assert np.any(view_anchored != view_global)

    assert np.all(view_anchored[int(size_on_pg[0]/2), int(size_on_pg[1]/2)] == ent_1.base_color)
 

def test_anchored_relative(shape):

    playground = EmptyPlayground()
    contour = Contour(shape=shape, radius=20)

    ent_1 = MockPhysical(contour=contour, mass=5, movable=True)
    playground.add(ent_1, ((0,0), 0))
    view_anchored_1 = AnchoredView(anchor=ent_1, size_on_playground=(200, 200))

    ent_2 = MockPhysical(contour=contour)
    playground.add(ent_2, ((50, 50), 0))
    view_anchored_2 = AnchoredView(anchor=ent_1, size_on_playground=(200, 200))
    
    img_orig_1 = view_anchored_1.update_view()
    img_orig_2 = view_anchored_2.update_view()

    for angle in range(1, contour.shape.value):

        ent_1.move_to(((0,0), angle*math.pi/contour.shape.value))
        img_rotated_1 = view_anchored_1.update_view()
        img_rotated_2 = view_anchored_2.update_view()

        assert np.all( img_rotated_2 == img_orig_2 )
        assert np.any( img_rotated_1 != img_orig_1 )

        
        
