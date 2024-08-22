from gymnasium import spaces

from spg.core.entity import Entity
from spg.core.entity.body import AttachedStaticMixin
from spg.core.entity.interaction.activable import ActivableMixin
from spg.core.entity.interaction.grasper import GrasperHold
from spg.core.entity.sprite import get_texture_from_geometry


class Trigger(Entity, ActivableMixin, AttachedStaticMixin):
    def __init__(self, **kwargs):

        texture, _ = get_texture_from_geometry(
            geometry="circle", radius=20, color=(255, 0, 0)
        )

        super().__init__(ghost=True, texture=texture, **kwargs)

        self.triggered = False

    def activate(self, entity, **kwargs):
        self.activated = True

    def pre_step(self):
        self.triggered = False
        super().pre_step()

    @property
    def attachment_point(self):
        return 0, 0

    @property
    def action_space(self):
        return spaces.Discrete(2)

    def apply_action(self, action):
        self.triggered = bool(action)


class GrasperHand(Entity, AttachedStaticMixin, GrasperHold):
    def __init__(self, grasper_radius, **kwargs):

        texture, _ = get_texture_from_geometry(
            geometry="circle", radius=grasper_radius, color=(255, 0, 0)
        )

        super().__init__(
            texture=texture,
            ghost=True,
            **kwargs,
        )

        GrasperHold.__init__(self)

    @property
    def attachment_point(self):
        return 0, 0
