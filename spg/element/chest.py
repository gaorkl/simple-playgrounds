from .element import PhysicalElement, RewardElement
from ..playground.collision import CollisionTypes


class Chest(PhysicalElement):
    def __init__(self, color=None):

        super().__init__(
            radius=15,
            filename=":spg:spg/goal.png",
            color=color,
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
