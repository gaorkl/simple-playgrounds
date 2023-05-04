from spg.definitions import CollisionTypes
from spg.entity import Entity, Element
from spg.entity.mixin import (
    ActivableMixin,
    AttachedStaticMixin,
    BaseDynamicMixin,
    BaseStaticMixin,
)
from tests.mock_entities import MockElement, MockStaticElement, MockDynamicElement


class MockActivable(Element, ActivableMixin):

    def __init__(self, **kwargs):
        super().__init__(
            filename=":resources:onscreen_controls/flat_light/play.png",
            **kwargs,
        )

    def activate(self, entity, **kwargs):
        self.activated = True


class ActivableMoving(MockActivable, BaseDynamicMixin):

    def __init__(self, **kwargs):
        super().__init__(mass=1, **kwargs)


class ActivableZone(MockActivable, BaseStaticMixin):

    def __init__(self, **kwargs):
        super().__init__(ghost=True, **kwargs)


class ActivableHalo(Entity, ActivableMixin, AttachedStaticMixin):

    def __init__(self, **kwargs):
        super().__init__(ghost=True, **kwargs)

    def activate(self, entity, **kwargs):
        self.activated = True

    @property
    def attachment_point(self):
        return 0, 0


class MockElementWithHalo(MockElement, BaseDynamicMixin):

    def __init__(self, interaction_radius=10, **kwargs):
        super().__init__(mass=10, **kwargs)

        halo_texture = self.sprite.texture
        halo_radius = self.radius + interaction_radius
        self.halo = ActivableHalo(texture=halo_texture, radius=halo_radius)

        self.add(self.halo)


class MockStaticTrigger(MockStaticElement):
    collision_type = CollisionTypes.TRIGGER


class MockDynamicTrigger(MockDynamicElement):
    collision_type = CollisionTypes.TRIGGER
