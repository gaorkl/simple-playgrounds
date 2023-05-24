import gc

import pytest

from spg.core.playground import EmptyPlayground
from tests.mock_entities import MockDynamicElement
from tests.mock_interactives import ActivableZone, MockElementWithHalo

coord_center = (0, 0), 0


@pytest.mark.parametrize("Elem", [MockDynamicElement, ActivableZone, MockElementWithHalo])
def test_gc_del(Elem):

    playground = EmptyPlayground(size=(100, 100))

    playground.add(Elem(), coord_center)

    del playground

    gc.collect()
    for obj in gc.get_objects():
        if isinstance(obj, EmptyPlayground):
            raise ValueError
        if isinstance(obj, Elem):
            raise ValueError
