import pytest

from spg.playground import EmptyPlayground
# Add test Interactions to collisions
from tests.mock_entities import MockStaticElement
from tests.mock_interactives import ActivableMoving, ActivableZone, MockElementWithHalo, MockDynamicTrigger, \
    MockStaticTrigger

coord_0 = ((0, 0), 0)

# teams of element 1 ; team of element 2 ; is interacting?


@pytest.fixture(
    scope="module",
    params=[
        ("team_0", "team_0", True),
        ("team_0", "team_1", False),
        (None, "team_0", True),
        (None, None, True),
        ("team_0", None, True),
        (["team_0", "team_1"], "team_0", True),
        ("team_0", ["team_0", "team_1"], True),
        ("team_0", ["team_2", "team_1"], False),
    ],
)
def team_params(request):
    return request.param


coord_center = ((0, 0), 0)
coord_shift = ((0, 1), 0)


@pytest.mark.parametrize("TestElement", [MockDynamicTrigger, MockStaticTrigger])
@pytest.mark.parametrize(
    "Activable", [ActivableMoving, ActivableZone, MockElementWithHalo]
)
def test_element_activates(TestElement, Activable, team_params):

    team_1, team_2, is_interacting = team_params

    playground = EmptyPlayground(size=(100, 100))

    elem = TestElement(teams=team_1)
    playground.add(elem, coord_center)

    activable = Activable(teams=team_2)
    playground.add(activable, coord_shift)

    playground.step(playground.null_action)

    if isinstance(activable, ActivableZone) and isinstance(elem, MockStaticElement):
        activated = False
    else:
        activated = True

    activated = activated and is_interacting

    if isinstance(activable, MockElementWithHalo):
        assert activable.halo.activated == activated
    else:
        assert activable.activated == activated
