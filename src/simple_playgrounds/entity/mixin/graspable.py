from typing import Optional, Any, TYPE_CHECKING
if TYPE_CHECKING:
    from simple_playgrounds.agent.parts import Part

from simple_playgrounds.entity.embodied import InteractionShape
from simple_playgrounds.common.definitions import CollisionTypes


class Grasper(InteractionShape):

    @staticmethod
    def _set_pm_collision_type(pm_shape):
        pm_shape.collision_type = CollisionTypes.GRASPER


class Graspable(InteractionShape):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self._grasped_by: Optional[Any] = None
        self._pm_visible_shape.collision_type = CollisionTypes.GRASPABLE

    def pre_step(self):
        self._grasped_by = None

    def grasp(self, part: Part):
        self._grasped_by = part

    @property
    def grasped_by(self):
        return self._grasped_by

    @property
    def grasped(self):
        return bool(self._grasped_by)

    @staticmethod
    def _set_pm_collision_type(pm_shape):
        pm_shape.collision_type = CollisionTypes.GRASPABLE