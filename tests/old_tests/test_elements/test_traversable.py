from simple_playgrounds.engine import Engine
from simple_playgrounds.playground.layouts import SingleRoom
from simple_playgrounds.element.elements.basic import Traversable, Physical


def test_traversable_physical():

    # non traversable vs non traversable
    playground = SingleRoom(size=(200, 200))

    elem_1 = Traversable(radius=20, movable=True, mass=5, config_key='circle')
    playground.add_element(elem_1, initial_coordinates=((100, 100), 0))

    elem_2 = Physical(radius=20, movable=True, mass=5, config_key='circle')
    playground.add_element(elem_2, initial_coordinates=((100, 100), 0))

    playground.update(10)
    playground.update(10)
    playground.update(10)

    assert elem_1.position == elem_2.position


def test_physical_physical():
    # non traversable vs non traversable
    playground = SingleRoom(size=(200, 200))

    elem_1 = Physical(radius=20, movable=True, mass=5, config_key='circle')
    playground.add_element(elem_1, initial_coordinates=((100, 100), 0))

    elem_2 = Physical(radius=20, movable=True, mass=5, config_key='circle')
    playground.add_element(elem_2, initial_coordinates=((100, 100), 0))

    playground.update(10)
    playground.update(10)
    playground.update(10)

    assert elem_1.position != elem_2.position


def test_traversable_traversable():
    # non traversable vs non traversable
    playground = SingleRoom(size=(200, 200))

    elem_1 = Traversable(radius=20, movable=True, mass=5, config_key='circle')
    playground.add_element(elem_1, initial_coordinates=((100, 100), 0))

    elem_2 = Traversable(radius=20, movable=True, mass=5, config_key='circle')
    playground.add_element(elem_2, initial_coordinates=((100, 100), 0))

    playground.update(10)
    playground.update(10)
    playground.update(10)

    assert elem_1.position == elem_2.position

