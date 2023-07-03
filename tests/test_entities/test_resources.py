from pathlib import Path

import pytest

from tests.mock_entities import MockPhysicalFromResource

coord_center = ((0, 0), 0)


def test_loading_spg_resources():

    MockPhysicalFromResource(filename=":spg:platformer/items/diamond_blue.png")


def test_loading_arcade_resources():

    MockPhysicalFromResource(filename=":resources:images/items/coinGold.png")


def test_loading_spg_resources_fail():

    with pytest.raises(FileNotFoundError):
        MockPhysicalFromResource(filename=":spg:platformer/items/gfdsgfsd.png")


def test_load_local_file():
    rabbit_path = Path(__file__).parent / "rabbit.png"
    MockPhysicalFromResource(filename=rabbit_path)
