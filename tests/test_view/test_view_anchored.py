import random
import math

import pytest
import pymunk

import numpy as np
from matplotlib.colors import to_rgb
from skimage import transform
from simple_playgrounds.common import view

from simple_playgrounds.playground.playground import EmptyPlayground
from simple_playgrounds.common.view import AnchoredView, FixedGlobalView
from simple_playgrounds.entity.embodied.contour import Contour

from ..mock_entities import MockPhysical

import matplotlib.pyplot as plt


def test_anchored(shape, position, angle, radius, size_on_pg):

    playground = EmptyPlayground()
    contour = Contour(shape=shape, radius=radius)
    ent_1 = MockPhysical(contour=contour, movable=True, mass=5, initial_coordinates=((0,0), 0)

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

    ent_1 = MockPhysical(contour=contour, mass=5, initial_coordinates=((0,0), 0, movable=True)
    playground.add(ent_1, ((0,0), 0))
    view_anchored_1 = AnchoredView(anchor=ent_1, draw_transparent=True, size_on_playground=(200, 200))

    ent_2 = MockPhysical(contour=contour)
    playground.add(ent_2, ((50, 50), 0))
    
    view_anchored_2 = AnchoredView(anchor=ent_2, draw_transparent=True, size_on_playground=(200, 200))
    
    for angle in range(1, contour.shape.value):

        angle_rad = angle*2*math.pi/contour.shape.value
        ent_1.move_to(((0,0), angle_rad ))
        img_rotated_1 = view_anchored_1.update_view()

        x, y = ent_2.position.rotated(-angle_rad).int_tuple
        r, c = 100-y, 100+x

        assert np.all(img_rotated_1[r, c] == ent_1.base_color)
