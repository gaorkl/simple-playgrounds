from ..entity import Graspable
from ..utils.definitions import CollisionTypes
from .element import PhysicalElement, RewardElement


class Diamond(PhysicalElement, RewardElement):
    def __init__(self, chest):

        super().__init__(
            mass=10,
            filename=":spg:platformer/items/diamond_green.png",
            radius=10,
        )

        grasp_halo = Graspable(anchor=self)
        self.add(grasp_halo)

        self.chest = chest

    def _set_pm_collision_type(self):
        for pm_shape in self._pm_shapes:
            pm_shape.collision_type = CollisionTypes.GEM

    @property
    def _base_reward(self) -> float:
        return 10
