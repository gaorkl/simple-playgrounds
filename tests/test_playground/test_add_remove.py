import pytest

from spg.core.playground import EmptyPlayground
from tests.mock_entities import (
    MockDynamicElement,
    MockElemWithAttachment,
    MockElemWithFixedAttachment,
    MockStaticElement,
)
from tests.mock_interactives import MockElementWithHalo

coord_center = (0, 0), 0


class MockPlayground(EmptyPlayground):
    def __init__(self, elem_cls, *args, **kwargs):
        self.elem_cls = elem_cls
        super().__init__(*args, **kwargs)

    def place_elements(self):
        self.elem = self.elem_cls()
        self.add(self.elem, coord_center)


# test for MockDynamicElement, MockStaticElement, MockElemWithFixedAttachment, MockElemWithAttachment
@pytest.mark.parametrize(
    "TestElement", [MockDynamicElement, MockStaticElement, MockElementWithHalo]
)
def test_playground_interface_basic_element(TestElement):
    playground = MockPlayground(TestElement, size=(100, 100))

    assert len(playground.elements) == 1
    assert playground.elem in playground.elements

    elem_2 = TestElement()
    playground.add(elem_2, coord_center)

    assert len(playground.elements) == 2
    assert elem_2 in playground.elements

    playground.remove(elem_2)
    assert len(playground.elements) == 1
    assert elem_2 not in playground.elements

    playground.remove(playground.elem)
    assert len(playground.elements) == 0
    assert playground.elem not in playground.elements

    assert not playground.space.shapes
    assert not playground.space.bodies

    playground.reset()

    assert len(playground.elements) == 1
    assert playground.elem in playground.elements
    assert elem_2 not in playground.elements


# test with MockElemWithFixedAttachment, MockElemWithAttachment
@pytest.mark.parametrize(
    "TestElement", [MockElemWithFixedAttachment, MockElemWithAttachment]
)
def test_playground_interface_attached_element(TestElement):

    playground = EmptyPlayground(size=(100, 100))

    elem_1 = TestElement((0, 0), 0)

    playground.add(elem_1, coord_center)

    assert len(playground.elements) == 1
    assert elem_1 in playground.elements

    elem_2 = TestElement((0, 0), 0)

    playground.add(elem_2, coord_center)
    assert len(playground.elements) == 2
    assert elem_2 in playground.elements

    playground.remove(elem_1)
    assert len(playground.elements) == 1

    playground.remove(elem_2)
    assert len(playground.elements) == 0

    assert not playground.space.shapes
    assert not playground.space.bodies

    playground.reset()

    assert len(playground.elements) == 0
    assert elem_1 not in playground.elements
    assert elem_2 not in playground.elements

    assert not playground.space.shapes
    assert not playground.space.bodies
