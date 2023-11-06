import gc
import weakref

import pytest

from spg.core.playground import EmptyPlayground
from tests.mock_entities import MockDynamicElement
from tests.mock_interactives import ActivableZone, MockElementWithHalo

coord_center = (0, 0), 0


@pytest.mark.parametrize(
    "Elem", [MockDynamicElement, ActivableZone, MockElementWithHalo]
)
def test_gc_del(Elem):

    playground = EmptyPlayground(size=(100, 100))
    elem = Elem()
    playground.add(elem, coord_center)

    weak_entity_ref = weakref.ref(elem)

    del playground
    del elem

    gc.collect()
    assert weak_entity_ref() is None

    # def test_garbage_collection_after_clear(self):
    #     entities = [Entity(name=f"Entity {i}") for i in range(3)]
    #     weak_refs = [weakref.ref(entity) for entity in entities]
    #     for entity in entities:
    #         self.playground.add_entity(entity)
    #
    #     # Delete all entities
    #     self.playground.delete_all_entities()
    #     del entities
    #     gc.collect()  # Force garbage collection
    #
    #     # Check that all weak references are now dead
    #     dead_refs = [ref for ref in weak_refs if ref() is None]
    #     self.assertEqual(len(dead_refs), len(weak_refs))
