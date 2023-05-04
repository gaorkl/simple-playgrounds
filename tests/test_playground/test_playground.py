import pytest

from spg.entity import Element
from spg.playground import Playground


class MockElemen2t(Element):
    def __init__(self, **kwargs):
        super().__init__(
            name="mock",
            filename=":resources:onscreen_controls/flat_light/play.png",
            **kwargs,
        )

    def pre_step(self):
        pass

    def post_step(self):
        pass

    @property
    def collision_type(self):
        return 0


class MockPlayground(Playground):
    def __init__(self):
        super().__init__(size=(100, 100))

    def place_agents(self):
        pass

    def place_elements(self):
        elem = MockElement()
        self.add(elem, ((10, 10), 0))


class MockPlaygroundOverlapping(Playground):
    def __init__(self, allow_overlapping: bool = False):
        self.allow_overlapping = allow_overlapping
        super().__init__(size=(100, 100))

    def place_agents(self):
        pass

    def place_elements(self):
        elem = MockElement()
        self.add(elem, ((10, 10), 0))

        elem = MockElement()
        self.add(elem, ((10, 10), 0), allow_overlapping=self.allow_overlapping)


def test_playground_basic():
    playground = MockPlayground()

    assert playground.size == (100, 100)
    assert playground

    # test that the playground has no agent and no element
    assert playground.agents == []
    assert playground.elements != []

    assert playground.space.bodies != []

    playground.reset()

    assert len(playground.elements) == 1


@pytest.mark.parametrize("allow_overlapping", [True, False])
def test_overlapping(allow_overlapping):
    if not allow_overlapping:
        with pytest.raises(ValueError):
            playground = MockPlaygroundOverlapping(allow_overlapping=allow_overlapping)

    else:
        playground = MockPlaygroundOverlapping(allow_overlapping=allow_overlapping)
        assert len(playground.elements) == 2
