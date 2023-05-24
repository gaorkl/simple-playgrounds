from spg.core.collision import CollisionTypes
from spg.core.entity import Element, Entity
from spg.core.entity.mixin import (
    ActivableMixin,
    AttachedStaticMixin,
    BaseDynamicMixin,
    BaseStaticMixin,
)
from tests.mock_entities import MockDynamicElement, MockElement, MockStaticElement


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


class ActivableZoneTeleport(ActivableZone):

    entities_to_move = []

    def __init__(self, teleport_coordinates, **kwargs):
        super().__init__(**kwargs)

        self.teleport_coordinates = teleport_coordinates

    def activate(self, entity, **kwargs):
        self.entities_to_move.append(entity.base)
        self.activated = True

    def pre_step(self):
        super().pre_step()
        self.activated = False
        self.entities_to_move = []

    def post_step(self):

        for entity in set(self.entities_to_move):
            self.entities_to_move.remove(entity)
            entity.move_to(self.teleport_coordinates)


class ActivableZoneRemove(ActivableZone):

    entities_to_remove = []

    def activate(self, entity, **kwargs):
        self.activated = True
        self.entities_to_remove.append(entity)

    def pre_step(self):
        super().pre_step()
        self.activated = False
        self.entities_to_remove = []

    def post_step(self):
        for entity in set(self.entities_to_remove):
            self.entities_to_remove.remove(entity)
            self.playground.remove(entity)
