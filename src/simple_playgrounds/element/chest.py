from simple_playgrounds.common.definitions import CollisionTypes
from simple_playgrounds.entity.physical import PhysicalEntity
from simple_playgrounds.playground.collision_handlers import grasper_grasps_graspable

from simple_playgrounds.playground.playground import Playground

from simple_playgrounds.common.position_utils import InitCoord
from simple_playgrounds.element.element import RewardElement


class Chest(PhysicalEntity):
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
        
        for part in entity.grasped_by:
            agent = part.agent
            agent.reward += entity.reward / len(entity.grasped_by)

        if not entity.grasped_by:
            agent = self._playground.get_closest_agent(self)

        self._playground.remove(entity)
