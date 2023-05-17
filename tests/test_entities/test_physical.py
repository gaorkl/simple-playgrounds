import math

import numpy as np
import pymunk
import pytest

from spg.playground import EmptyPlayground
from tests.mock_entities import (
    DynamicElementFromGeometry,
    MockDynamicElement,
    MockStaticElement,
    MockStaticElementFromTexture,
    NonConvexC,
    NonConvexPlus,
    NonConvexPlus_Approx,
    StaticElementFromGeometry,
)

coord_center = (0, 0), 0
coord_shift = (0, 1), 0.3


@pytest.mark.parametrize("TestElem", [MockDynamicElement, MockStaticElement])
def test_add_remove_dynamic_entity(TestElem):
    playground = EmptyPlayground(size=(10, 10))

    ent_1 = TestElem()
    playground.add(ent_1, coord_center)

    assert ent_1 in playground.elements
    assert ent_1 not in playground.agents

    playground.remove(ent_1)

    assert ent_1 not in playground.elements

    playground.reset()
    assert ent_1 not in playground.elements


@pytest.mark.parametrize(
    "TestElem", [StaticElementFromGeometry, DynamicElementFromGeometry]
)
@pytest.mark.parametrize("radius", [2, 3, 4, 5, 10, 20])
def test_size_entities_radius(radius, TestElem):
    playground = EmptyPlayground(size=(100, 100))
    ent_1 = TestElem(geometry="circle", radius=radius, color=(0, 0, 1))
    playground.add(ent_1, coord_center)

    assert ent_1.radius == pytest.approx(radius, 1)
    assert ent_1.height == ent_1.width == pytest.approx(math.sqrt(2) * radius, 1)


@pytest.mark.parametrize("radius", [2, 3, 4, 5, 10, 20])
def test_circle_texture(radius):
    playground = EmptyPlayground(size=(100, 100))
    ent_1 = StaticElementFromGeometry(geometry="circle", radius=10, color=(0, 0, 1))
    playground.add(ent_1, coord_center)

    assert ent_1.texture is not None


# test rectangle with variations of size
@pytest.mark.parametrize("size", [(10, 10), (5, 30)])
def test_size_entities_rectangle(size):
    playground = EmptyPlayground(size=(100, 100))
    ent_1 = StaticElementFromGeometry(geometry="rectangle", size=size, color=(0, 0, 1))
    playground.add(ent_1, coord_center)

    assert ent_1.height == pytest.approx(size[0], 1)
    assert ent_1.width == pytest.approx(size[1], 1)


# test polygon with variations of vertices
@pytest.mark.parametrize("vertices", [3, 4, 5, 6])
def test_size_entities_polygon(vertices):
    playground = EmptyPlayground(size=(100, 100))

    # get regular vertices centered at (0, 0) as a np array
    vertices = np.array(
        [
            (
                math.cos(2 * math.pi * i / vertices) * 30,
                math.sin(2 * math.pi * i / vertices) * 30,
            )
            for i in range(vertices)
        ]
    )

    ent_1 = StaticElementFromGeometry(
        geometry="polygon", vertices=vertices, color=(0, 0, 1)
    )
    playground.add(ent_1, coord_center)


@pytest.mark.parametrize("vertices", [4, 5, 6])
@pytest.mark.parametrize("offset", [(0, 0), (10, 10), (-20, 20)])
def test_polygon_offset(vertices, offset):
    playground = EmptyPlayground(size=(100, 100))

    x_offset, y_offset = offset
    # get regular vertices centered at (x_offset, y_offset) as a np array
    vertices = np.array(
        [
            (
                math.cos(2 * math.pi * i / vertices) * 20 + x_offset,
                math.sin(2 * math.pi * i / vertices) * 20 + y_offset,
            )
            for i in range(vertices)
        ]
    )

    ent_1 = StaticElementFromGeometry(
        geometry="polygon", vertices=vertices, color=(0, 0, 1)
    )
    coord_offset = (x_offset, y_offset), 0
    playground.add(ent_1, (ent_1.offset, 0))

    assert (
        playground.space.point_query(
            offset, max_distance=1, shape_filter=pymunk.ShapeFilter()
        )
        != []
    )
    assert (
        playground.space.point_query(
            (x_offset + 30, y_offset + 30),
            max_distance=1,
            shape_filter=pymunk.ShapeFilter(),
        )
        == []
    )


def test_setting_entity_by_positions():
    playground = EmptyPlayground(size=(200, 200))

    vertices = np.array([(30, 30), (50, 30), (50, 10), (80, 40), (60, 70)])
    ent_1 = StaticElementFromGeometry(
        geometry="polygon", vertices=vertices, color=(0, 0, 125)
    )

    coord_offset = (ent_1.offset, 0)

    playground.add(ent_1, coord_offset)

    assert ent_1.coordinates == coord_offset

    query_points_false = ((20, 20), (40, 20), (70, 20), (70, 60), (50, 60))

    for point in query_points_false:
        assert (
            playground.space.point_query(
                point, max_distance=1, shape_filter=pymunk.ShapeFilter()
            )
            == []
        )

    # TODO more points
    query_points_true = ((60, 40),)

    for point in query_points_true:
        assert (
            playground.space.point_query(
                point, max_distance=1, shape_filter=pymunk.ShapeFilter()
            )
            != []
        )


def test_fixed_dont_move():
    playground = EmptyPlayground(size=(100, 100))

    ent_1 = MockStaticElement()
    playground.add(ent_1, coord_center)

    ent_2 = MockStaticElement()
    playground.add(ent_2, coord_shift)

    playground.step(playground.null_action)

    assert ent_1.coordinates == coord_center
    assert ent_2.coordinates == coord_shift


def test_fix_moves_movable():
    playground = EmptyPlayground(size=(100, 100))

    ent_1 = MockStaticElement()
    playground.add(ent_1, coord_center)

    ent_2 = MockDynamicElement()
    playground.add(ent_2, coord_shift)

    playground.step(playground.null_action)

    assert ent_1.coordinates == coord_center
    assert ent_2.coordinates != coord_shift


@pytest.mark.parametrize("traversable", [True, False])
def test_fix_dont_move_traversable(traversable):
    playground = EmptyPlayground(size=(100, 100))

    ent_1 = MockStaticElement()
    playground.add(ent_1, coord_center)

    ent_2 = MockDynamicElement(traversable=traversable)
    playground.add(ent_2, coord_shift)

    playground.step(playground.null_action)

    assert ent_1.coordinates == coord_center

    if traversable:
        assert ent_2.coordinates == coord_shift
    else:
        assert ent_2.coordinates != coord_shift


def test_moving_moves_movable():
    playground = EmptyPlayground(size=(100, 100))

    ent_1 = MockDynamicElement()
    playground.add(ent_1, coord_center)

    ent_2 = MockDynamicElement()
    playground.add(ent_2, coord_shift)

    playground.step(playground.null_action)

    assert ent_1.coordinates != coord_center
    assert ent_2.coordinates != coord_shift


def test_non_convex_entity():
    playground = EmptyPlayground(size=(100, 100))

    ent_1 = NonConvexPlus(40, 10, mass=1)
    playground.add(ent_1, coord_center)

    ent_2 = NonConvexC(60, 20, mass=1)

    playground.add(ent_2, coord_center)

    for _ in range(100):
        playground.step(playground.null_action)

    assert ent_1.coordinates == coord_center
    assert ent_2.coordinates == coord_center


def test_non_convex_entity_moving():
    playground = EmptyPlayground(size=(100, 100))

    ent_1 = NonConvexPlus(40, 10, mass=1)
    playground.add(ent_1, coord_center)
    ent_2 = NonConvexC(40, 20, mass=1)
    playground.add(ent_2, coord_shift)

    playground.step(playground.null_action)

    assert ent_1.coordinates != coord_center
    assert ent_2.coordinates != coord_shift


@pytest.mark.parametrize("shape_approx", ["circle", "box", "hull", "decomposition"])
def test_shape_approximation(shape_approx):
    playground = EmptyPlayground(size=(100, 100))

    coord = ((10, 10), math.pi / 3)
    ent_1 = NonConvexPlus_Approx(20, 10, shape_approximation=shape_approx, mass=1)

    playground.add(ent_1, coord)


@pytest.mark.parametrize("radius", [10, 20, 30])
@pytest.mark.parametrize("vertices", [3, 4, 5])
def test_entity_size(vertices, radius):

    playground = EmptyPlayground(size=(100, 100))

    # get regular vertices centered at (0, 0) as a np array
    vertices = np.array(
        [
            (
                math.cos(2 * math.pi * i / vertices) * radius,
                math.sin(2 * math.pi * i / vertices) * radius,
            )
            for i in range(vertices)
        ]
    )

    ent_1 = StaticElementFromGeometry(
        geometry="polygon", vertices=vertices, color=(0, 0, 1)
    )
    playground.add(ent_1, coord_center)

    assert ent_1.radius == pytest.approx(radius, rel=0.2)


@pytest.mark.parametrize("radius", [2, 3, 4, 5, 10, 20])
@pytest.mark.parametrize("base_radius", [2, 3, 4, 5, 10, 20])
def test_size_entities_radius(radius, base_radius):

    base_entity = StaticElementFromGeometry(
        geometry="circle", radius=base_radius, color=(0, 0, 1)
    )

    texture = base_entity.texture

    ent_1 = MockStaticElementFromTexture(
        texture=texture, radius=radius, color=(0, 0, 1)
    )

    assert ent_1.radius == pytest.approx(radius, 1)
    assert ent_1.height == ent_1.width == pytest.approx(math.sqrt(2) * radius, 1)
    assert ent_1.sprite.height / ent_1.sprite.scale == base_entity.sprite.height


# test rectangle with variations of size
@pytest.mark.parametrize("scale", [0.5, 1, 5, 10])
def test_entity_scale(scale):

    ent_base = MockDynamicElement()
    radius_base = ent_base.radius

    ent_1 = MockDynamicElement(radius=radius_base * scale)

    assert ent_1.radius == pytest.approx(radius_base * scale, rel=0.2)


def test_small_triangle():

    playground = EmptyPlayground(size=(100, 100))

    vertices = 3
    radius = 10

    # get regular vertices centered at (0, 0) as a np array
    vertices = np.array(
        [
            (
                math.cos(2 * math.pi * i / vertices) * radius,
                math.sin(2 * math.pi * i / vertices) * radius,
            )
            for i in range(vertices)
        ]
    )

    ent_1 = DynamicElementFromGeometry(
        geometry="polygon", vertices=vertices, color=(0, 0, 255)
    )
    playground.add(ent_1, coord_center)

    # plt_draw(playground)
    # plt.imshow(ent_1.texture.image)
    # plt.show()

    assert playground.space.point_query(
        (0, 0), max_distance=0, shape_filter=pymunk.ShapeFilter()
    )
