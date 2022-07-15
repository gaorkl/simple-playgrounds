import pytest
from simple_playgrounds.playground.playground import EmptyPlayground
from tests.mock_entities import MockPhysicalFromResource


def test_loading_spg_resources():

    playground = EmptyPlayground()
    element = MockPhysicalFromResource(
        playground, ((0, 0), 0), filename=":spg:platformer/items/diamond_blue.png"
    )


def test_loading_spg_resources_fail():

    playground = EmptyPlayground()

    with pytest.raises(FileNotFoundError):
        element = MockPhysicalFromResource(
            playground, ((0, 0), 0), filename=":spg:platformer/items/gfdsgfsd.png"
        )


def test_load_local_file():
    playground = EmptyPlayground()
    element = MockPhysicalFromResource(
        playground, ((0, 0), 0), filename="tests/test_misc/rabbit.png"
    )
