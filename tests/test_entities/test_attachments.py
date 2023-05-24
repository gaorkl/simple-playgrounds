import math

import pytest

from spg.core.playground import EmptyPlayground
from tests.mock_entities import MockElemWithAttachment, MockElemWithFixedAttachment

coord_center = (0, 0), 0
coord_shift = (0, 1), 0.3
coord_far = (10, 10), math.pi / 3


@pytest.mark.parametrize("relative_angle", [0, math.pi / 2, math.pi, 3 * math.pi / 2])
@pytest.mark.parametrize("anchor_point", [(0, 0), (5, 5), (-10, 10)])
def test_attached_elem(anchor_point, relative_angle):
    playground = EmptyPlayground(size=(100, 100))

    ent_1 = MockElemWithAttachment(
        anchor_point=anchor_point, relative_angle=relative_angle
    )
    playground.add(ent_1, coord_center)

    for _ in range(100):

        impulse = playground.np_random.uniform(-1, 1, size=2).tolist()
        angular = playground.np_random.uniform(-1, 1)

        ent_1.pm_body.apply_impulse_at_local_point(impulse, (0, 0))
        ent_1.pm_body.angular_velocity = angular

        playground.step(playground.null_action)

    assert ent_1.position != (0, 0)
    assert ent_1.angle != 0

    position_anchor = ent_1.pm_body.local_to_world(
        ent_1.attachment_points[ent_1.arm][0]
    )

    dist = position_anchor.get_dist_sqrd(ent_1.arm.pm_body.position)
    assert pytest.approx(dist, rel=1e3) == ent_1.arm.radius**2


@pytest.mark.parametrize(
    "TestElem", [MockElemWithAttachment, MockElemWithFixedAttachment]
)
@pytest.mark.parametrize("relative_angle", [0, math.pi / 2, math.pi, 3 * math.pi / 2])
@pytest.mark.parametrize("anchor_point", [(0, 0), (5, 5), (-10, 10)])
def test_attached_static_move(anchor_point, relative_angle, TestElem):
    playground = EmptyPlayground(size=(100, 100))

    ent_1 = TestElem(anchor_point=anchor_point, relative_angle=relative_angle)

    playground.add(ent_1, coord_center)

    orig_center_gravity = ent_1.arm.pm_shapes[0].bb

    for _ in range(100):

        impulse = playground.np_random.uniform(-1, 1, size=2).tolist()
        angular = playground.np_random.uniform(-1, 1)

        ent_1.pm_body.apply_impulse_at_local_point(impulse, (0, 0))
        ent_1.pm_body.angular_velocity = angular

        playground.step(playground.null_action)

    assert ent_1.position != (0, 0)
    assert ent_1.angle != 0

    assert ent_1.arm.pm_shapes[0].bb != orig_center_gravity
