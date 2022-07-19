from simple_playgrounds.playground.playgrounds.simple import WallClosedPG

from tests.mock_entities import (
    NonConvexPlus,
    NonConvexC,
)


def test_non_convex_entity():

    playground = WallClosedPG(size=(400, 400))

    NonConvexPlus(playground, ((-150, 100), 0), 20, 10, shape_approximation="circle")
    NonConvexPlus(playground, ((-50, 100), 0), 20, 10, shape_approximation="box")
    NonConvexPlus(playground, ((50, 100), 0), 20, 10, shape_approximation="hull")
    NonConvexPlus(
        playground, ((150, 100), 0), 20, 10, shape_approximation="decomposition"
    )

    NonConvexC(playground, ((-150, -100), 0), 20, 10, shape_approximation="circle")
    NonConvexC(playground, ((-50, -100), 0), 20, 10, shape_approximation="box")
    NonConvexC(playground, ((50, -100), 0), 20, 10, shape_approximation="hull")
    NonConvexC(
        playground, ((150, -100), 0), 20, 10, shape_approximation="decomposition"
    )
