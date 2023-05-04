import pytest

from spg.playground import Playground
from tests.mock_entities import MockPhysicalFromResource

coord_center = ((0, 0), 0)


def test_loading_spg_resources():

    playground = Playground()
    element = MockPhysicalFromResource(
        filename=":spg:platformer/items/diamond_blue.png"
    )
    playground.add(element, coord_center)


def test_loading_spg_resources_fail():

    with pytest.raises(FileNotFoundError):
        MockPhysicalFromResource(filename=":spg:platformer/items/gfdsgfsd.png")


def test_load_local_file():
    playground = Playground()
    element = MockPhysicalFromResource(filename="tests/test_playground/rabbit.png")
    playground.add(element, coord_center)
