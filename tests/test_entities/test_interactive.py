import pytest

from spg.core.playground import Playground
from tests.mock_interactives import (
    ActivableMoving,
    ActivableZone,
    ActivableZoneRemove,
    ActivableZoneTeleport,
    MockDynamicTrigger,
    MockElementWithHalo,
    MockStaticTrigger,
)

coord_center = (0, 0), 0
coord_shift = (0, 1), 0.3
coord_far = (50, 50), 0


def test_activable_element_activates_zone():
    playground = Playground(size=(100, 100))

    elem = ActivableMoving()
    playground.add(elem, coord_center)

    zone = ActivableZone()
    playground.add(zone, coord_shift)

    playground.step(playground.null_action)

    assert zone.activated


# test for TestElement in [MockDynamicElement, MockStaticElement]


@pytest.mark.parametrize("TestElement", [MockDynamicTrigger, MockStaticTrigger])
@pytest.mark.parametrize(
    "Activable", [ActivableMoving, ActivableZone, MockElementWithHalo]
)
def test_element_activates(TestElement, Activable):
    playground = Playground(size=(100, 100))

    elem = TestElement()
    playground.add(elem, coord_center)

    activable = Activable()
    playground.add(activable, coord_shift)

    playground.step(playground.null_action)

    if isinstance(activable, ActivableZone) and isinstance(elem, MockStaticTrigger):
        activated = False
    else:
        activated = True

    if isinstance(activable, MockElementWithHalo):
        assert activable.halo.activated == activated
    else:
        assert activable.activated == activated


def test_halo_doesnt_activate_itself():
    playground = Playground(size=(200, 200))

    elem = MockElementWithHalo()
    playground.add(elem, coord_center)

    playground.step(playground.null_action)

    assert not elem.halo.activated


@pytest.mark.parametrize("TestElement", [ActivableMoving, ActivableZone])
def test_far_doesnt_activate(TestElement):
    playground = Playground(size=(200, 200))

    elem = MockDynamicTrigger(radius=10)
    playground.add(elem, coord_center)

    activ = TestElement(radius=10)
    playground.add(activ, coord_far)

    playground.step(playground.null_action)

    assert not activ.activated


@pytest.mark.parametrize("angle", [0, 0.5, 1])
@pytest.mark.parametrize("position", [(0, 0), (50, 50), (-100, 100)])
def test_activate_move(angle, position):
    playground = Playground(size=(200, 200))

    elem = MockDynamicTrigger()
    playground.add(elem, coord_center)

    activ = ActivableZoneTeleport(teleport_coordinates=(position, angle))
    playground.add(activ, coord_shift)

    playground.step(playground.null_action)

    assert elem.position == position
    assert elem.angle == angle

    assert activ.activated


def test_activate_remove():
    playground = Playground(size=(200, 200))

    elem = MockDynamicTrigger()
    playground.add(elem, coord_center)

    activ = ActivableZoneRemove()
    playground.add(activ, coord_shift)

    playground.step(playground.null_action)

    assert elem not in playground.elements
    assert activ.activated
