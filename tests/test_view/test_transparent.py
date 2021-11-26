import numpy as np

from simple_playgrounds.playground.playground import EmptyPlayground
from ..mock_entities import MockPhysical


def test_transparent(custom_contour):
    playground = EmptyPlayground()
    view_empty = playground.view((0, 0), (50, 50))

    ent_1 = MockPhysical(contour=custom_contour, transparent=True, movable=True, mass=5)
    playground.add(ent_1, ((10, 10), 0))
    view_transparent = playground.view((0, 0), (50, 50))
    assert np.all(view_transparent == view_empty)

    view_transparent_visible = playground.view((0, 0), (50, 50), draw_invisible=True)
    assert not np.all(view_transparent == view_transparent_visible)
