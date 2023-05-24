import pytest

from spg.core.playground import EmptyPlayground
from tests.mock_agents import StaticAgent
from tests.mock_entities import MockDynamicElement


def test_default_name():
    playground = EmptyPlayground(size=(100, 100))

    elem = MockDynamicElement()
    assert elem.name is None

    playground.add(elem, ((0, 0), 0))

    assert elem.name is not None
    assert elem.name.split('_')[0] == "MockDynamicElement"


def test_custom_name():
    playground = EmptyPlayground(size=(100, 100))

    elem = MockDynamicElement(name="test_name")
    assert elem.name == "test_name"

    playground.add(elem, ((0, 0), 0))

    assert elem.name == "test_name"


def test_two_elem_with_same_name():
    playground = EmptyPlayground(size=(100, 100))

    elem_1 = MockDynamicElement(name="test_name")
    elem_2 = MockDynamicElement(name="test_name")

    playground.add(elem_1, ((0, 0), 0))
    playground.add(elem_2, ((0, 0), 0))


def test_two_agents_with_same_name():
    playground = EmptyPlayground(size=(100, 100))

    agent_1 = StaticAgent(name="test_name")
    agent_2 = StaticAgent(name="test_name")

    playground.add(agent_1, ((0, 0), 0))

    with pytest.raises(ValueError):
        playground.add(agent_2, ((0, 0), 0))
