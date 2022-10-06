from spg.playground import Room
from tests.mock_entities import NonConvexPlus


def test_non_convex_entity():

    playground = Room(size=(400, 400))

    nc_ent = NonConvexPlus(20, 10, shape_approximation="circle")
    playground.add(nc_ent, ((-150, 100), 0))

    nc_ent = NonConvexPlus(20, 10, shape_approximation="box")
    playground.add(nc_ent, ((-50, 100), 0))

    nc_ent = NonConvexPlus(20, 10, shape_approximation="hull")
    playground.add(nc_ent, ((50, 100), 0))

    nc_ent = NonConvexPlus(20, 10, shape_approximation="decomposition")
    playground.add(nc_ent, ((150, 100), 0))

    nc_ent = NonConvexPlus(20, 10, shape_approximation="circle")
    playground.add(nc_ent, ((-150, -100), 0))

    nc_ent = NonConvexPlus(20, 10, shape_approximation="box")
    playground.add(nc_ent, ((-50, -100), 0))

    nc_ent = NonConvexPlus(20, 10, shape_approximation="hull")
    playground.add(nc_ent, ((50, -100), 0))

    nc_ent = NonConvexPlus(20, 10, shape_approximation="decomposition")
    playground.add(nc_ent, ((150, -100), 0))
