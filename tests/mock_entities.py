# import numpy as np
# import pymunk
#
# from spg.elements import ColorWall, PhysicalElement, ZoneElement
# from spg.entity import InteractiveAnchored
# from spg.playground import get_colliding_entities

import numpy as np
import pymunk
from arcade.texture import Texture
from PIL import Image
from skimage import draw, morphology

from spg.components.elements.barrier import BarrierMixin
from spg.core.entity import Element, Entity
from spg.core.entity.mixin import (
    AttachedDynamicMixin,
    AttachedStaticMixin,
    BaseDynamicMixin,
    BaseStaticMixin,
)
from spg.core.entity.mixin.sprite import get_texture_from_geometry


class MockElement(Element):
    def __init__(self, **kwargs):
        super().__init__(
            filename=":resources:onscreen_controls/flat_light/play.png",
            **kwargs,
        )


class MockStaticElementFromTexture(Element, BaseStaticMixin):
    pass


class MockDynamicElement(MockElement, BaseDynamicMixin):
    def __init__(self, **kwargs):
        super().__init__(mass=1, **kwargs)


class MockStaticElement(MockElement, BaseStaticMixin):
    pass


class ElementFromGeometry(Element):
    def __init__(self, **kwargs):

        texture, offset = get_texture_from_geometry(**kwargs)
        self.offset = offset

        super().__init__(texture=texture, shape_approximation="decomposition", **kwargs)


class StaticElementFromGeometry(ElementFromGeometry, BaseStaticMixin):
    pass


class DynamicElementFromGeometry(ElementFromGeometry, BaseDynamicMixin):
    def __init__(self, **kwargs):
        super().__init__(mass=1, **kwargs)


class NonConvexPlus_Approx(Element, BaseDynamicMixin):
    def __init__(
        self,
        radius,
        width,
        **kwargs,
    ):
        img = np.zeros((2 * radius + 2 * width + 1, 2 * radius + 2 * width + 1, 4))

        rr, cc = draw.line(width, radius + width, width + 2 * radius, radius + width)
        img[rr, cc, :] = 1

        rr, cc = draw.line(radius + width, width, radius + width, width + 2 * radius)
        img[rr, cc, :] = 1

        for _ in range(int(width / 2) - 1):
            img = morphology.binary_dilation(img)

        PIL_image = Image.fromarray(np.uint8(img * 255)).convert("RGBA")

        texture = Texture(
            name=f"PLus_{radius}_{width}",
            image=PIL_image,
            hit_box_algorithm="Detailed",
            hit_box_detail=1,
        )

        super().__init__(
            texture=texture,
            **kwargs,
        )


class NonConvexPlus(NonConvexPlus_Approx):
    def __int__(self):
        super().__init__(shape_approximation="decomposition")


class NonConvexC(Element, BaseDynamicMixin):
    def __init__(
        self,
        radius,
        width,
        **kwargs,
    ):
        img = np.zeros((2 * radius + 2 * width + 1, 2 * radius + 2 * width + 1, 4))

        rr, cc = draw.circle_perimeter(radius + width, radius + width, radius)
        img[rr, cc, :] = 1

        rr, cc = draw.polygon(
            (0, 0, radius + width), (0, 2 * radius + 2 * width, radius + width)
        )
        img[rr, cc, :] = 0

        for _ in range(int(width / 2) - 1):
            img = morphology.binary_dilation(img)

        PIL_image = Image.fromarray(np.uint8(img * 255)).convert("RGBA")

        texture = Texture(
            name=f"C_{radius}_{width}",
            image=PIL_image,
            hit_box_algorithm="Detailed",
            hit_box_detail=1,
        )

        super().__init__(
            texture=texture,
            shape_approximation="decomposition",
            **kwargs,
        )


class MockAttachment(Entity, AttachedDynamicMixin):
    def __init__(self, **kwargs):
        super().__init__(
            mass=1,
            filename=":resources:images/topdown_tanks/tankBlue_barrel3_outline.png",
            sprite_front_is_up=True,
            **kwargs,
        )

    def _get_joint(self):
        joint = pymunk.PivotJoint(
            self.anchor.pm_body,
            self.pm_body,
            self.anchor.attachment_points[self][0],
            self.attachment_point,
        )
        joint.collide_bodies = False
        return joint

    @property
    def attachment_point(self):
        return -self.radius, 0


class MockFixedAttachment(Entity, AttachedStaticMixin):
    def __init__(self, **kwargs):
        super().__init__(
            filename=":resources:images/topdown_tanks/tankBlue_barrel3_outline.png",
            sprite_front_is_up=True,
            **kwargs,
        )

    @property
    def attachment_point(self):
        return -self.radius, 0


class MockElemWithAttachment(MockDynamicElement):
    def __init__(self, anchor_point, relative_angle, **kwargs):

        super().__init__(**kwargs)

        self.arm = MockAttachment()
        self.add(self.arm, anchor_point, relative_angle)


class MockElemWithFixedAttachment(MockDynamicElement):
    def __init__(self, anchor_point, relative_angle, **kwargs):

        super().__init__(**kwargs)

        self.arm = MockFixedAttachment()
        self.add(self.arm, anchor_point, relative_angle)


class MockBarrier(MockStaticElement, BarrierMixin):
    pass


class MockPhysicalFromResource(Element, BaseStaticMixin):
    pass
