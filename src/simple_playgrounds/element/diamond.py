from simple_playgrounds.common.definitions import CollisionTypes
from simple_playgrounds.element.element import RewardElement
from simple_playgrounds.entity.interactive import Graspable


from simple_playgrounds.playground.playground import Playground

from simple_playgrounds.common.position_utils import InitCoord


class Diamond(RewardElement):
    def __init__(self, chest):

        super().__init__(
            mass=10,
            filename=":spg:platformer/items/diamond_green.png",
            radius=10,
        )

        Graspable(self)
        self.chest = chest

    def _set_pm_collision_type(self):
        for pm_shape in self._pm_shapes:
            pm_shape.collision_type = CollisionTypes.GEM

    @property
    def _base_reward(self) -> float:
        return 10
