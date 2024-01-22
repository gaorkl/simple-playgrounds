import gc
import weakref

import pytest

from spg.core.playground import Playground
from tests.mock_entities import MockDynamicElement
from tests.mock_interactives import ActivableZone, MockElementWithHalo

coord_center = (0, 0), 0


@pytest.mark.parametrize(
    "Elem", [MockDynamicElement, ActivableZone, MockElementWithHalo]
)
def test_gc_del(Elem):

    playground = Playground(size=(100, 100))
    elem = Elem()
    playground.add(elem, coord_center)

    weak_entity_ref = weakref.ref(elem)

    del playground
    del elem

    gc.collect()
    assert weak_entity_ref() is None

    for obj in gc.get_objects():
        if isinstance(obj, Playground):
            raise AssertionError("Playground is not deleted")
        if isinstance(obj, Elem):
            raise AssertionError("Element is not deleted")


def test_gc_del_fixtures(dummy_pg):
    weak_pg_ref = weakref.ref(dummy_pg)

    del dummy_pg

    gc.collect()

    for obj in gc.get_objects():
        if isinstance(obj, Playground):
            raise AssertionError("Playground is not deleted")


@pytest.mark.parametrize(
    "Elem", [MockDynamicElement, ActivableZone, MockElementWithHalo]
)
def test_gc_del(Elem):
    class PgGcTest(Playground):
        pass

    class ElemGcTest(Elem):
        pass

    playground = PgGcTest(size=(100, 100))
    elem = ElemGcTest()
    playground.add(elem, coord_center)

    del playground
    del elem

    gc.collect()

    for obj in gc.get_objects():
        if isinstance(obj, PgGcTest):
            raise AssertionError("Playground is not deleted")
        if isinstance(obj, ElemGcTest):
            raise AssertionError("Element is not deleted")
