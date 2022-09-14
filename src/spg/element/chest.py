from ..utils.definitions import CollisionTypes
from .element import PhysicalElement, RewardElement


class Chest(PhysicalElement):
    def __init__(self):

        super().__init__(
            radius=15,
            filename=":spg:platformer/tiles/block_red.png",
        )

    def _set_pm_collision_type(self):
        for pm_shape in self._pm_shapes:
            pm_shape.collision_type = CollisionTypes.ACTIVABLE_BY_GEM

    def activate(self, entity: RewardElement):

        assert self._playground

        if entity.graspable:
            for grasper in entity.grasped_by:
                agent = grasper.anchor.agent
                agent.reward += entity.reward / len(entity.grasped_by)

        else:
            agent = self._playground.get_closest_agent(self)
            agent.reward += entity.reward

        self._playground.remove(entity)
