import pytest

from typing import Optional

from simple_playgrounds.entity import PhysicalEntity, AnchoredInteractive, StandAloneInteractive
from simple_playgrounds.common.position_utils import Coordinate
from simple_playgrounds.common.contour import Contour
from simple_playgrounds.common.definitions import CollisionTypes

contour = Contour('circle', 10, None, None)


class MockPhysical(PhysicalEntity):
    def move_to_position(self,
                         coordinates: Optional[Coordinate] = None,
                         **kwargs):
        self.coordinates = coordinates

    def update(self):
        pass


@pytest.fixture(scope="function")
def physical_basic():
    return MockPhysical(traversable=False,
                        transparent=False,
                        **contour._asdict(),
                        texture=(10, 100, 100),
                        movable=True, mass=5)


physical_basic_2 = physical_basic


@pytest.fixture(scope="function")
def physical_traversable():
    return MockPhysical(traversable=True,
                        transparent=False,
                        **contour._asdict(),
                        texture=(10, 100, 100),
                        movable=True, mass=5)


physical_traversable_2 = physical_traversable


@pytest.fixture(scope="function")
def physical_transparent():
    return MockPhysical(traversable=False,
                        transparent=True,
                        **contour._asdict(),
                        texture=(10, 100, 100),
                        movable=True, mass=5)


