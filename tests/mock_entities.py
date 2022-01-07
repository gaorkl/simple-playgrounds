from typing import Optional, TYPE_CHECKING

import pymunk

from simple_playgrounds.entity.embodied.interactive import StandAloneInteractive, AnchoredInteractive
from simple_playgrounds.entity.embodied.physical import PhysicalEntity
from simple_playgrounds.common.definitions import CollisionTypes, PymunkCollisionCategories
from simple_playgrounds.playground.collision_handlers import get_colliding_entities
from simple_playgrounds.entity.embodied.appearance.texture import ColorTexture
from simple_playgrounds.agent.agent import Agent


class MockPhysical(PhysicalEntity):

    def __init__(self, **kwargs):
        super().__init__(appearance=ColorTexture(color=(121, 10, 220)), **kwargs)

    def post_step(self):
        pass

    def _set_pm_collision_type(self):
        pass

class MockHaloTrigger(AnchoredInteractive):

    def __init__(self, **kwargs):
        super().__init__(appearance=ColorTexture(color=(121, 10, 220)), **kwargs)
        self.activated = False

    def pre_step(self):
        self.activated = False

    def post_step(self):
        pass

    def reset(self):
        pass

    def _set_pm_collision_type(self):
        self._pm_shape.collision_type = CollisionTypes.TEST_TRIGGER

    def trigger(self):
        self.activated = True


class MockHaloTriggered(MockHaloTrigger):

    def _set_pm_collision_type(self):
        self._pm_shape.collision_type = CollisionTypes.TEST_TRIGGERED


class MockZoneTrigger(StandAloneInteractive):

    def __init__(self, **kwargs):
        super().__init__(appearance=ColorTexture(color=(121, 10, 220)), **kwargs)
        self.activated = False

    def _set_pm_collision_type(self):
        self._pm_shape.collision_type = CollisionTypes.TEST_TRIGGER

    def pre_step(self):
        self.activated = False

    def post_step(self):
        pass

    def reset(self):
        pass

    def trigger(self):
        self.activated = True


class MockZoneTriggered(MockZoneTrigger):

    def _set_pm_collision_type(self):
        self._pm_shape.collision_type = CollisionTypes.TEST_TRIGGERED


class MockBarrier(PhysicalEntity):

    def __init__(self, **kwargs):
        super().__init__(appearance=ColorTexture(color=(121, 10, 220)), **kwargs)

    def update_team_filter(self):

        if not self._teams:
            return

        categ = 0
        for team in self._teams:
            categ = categ | 2 ** self._playground.teams[team]

        mask = pymunk.ShapeFilter.ALL_MASKS() ^ 2**PymunkCollisionCategories.DEFAULT
        for team in self._playground.teams:

            if team in self._teams:
                # mask = mask | 2 ** self._playground.teams[team]
                mask = mask ^ 2 ** self._playground.teams[team]

        self._pm_shape.filter = pymunk.ShapeFilter(categories=categ, mask=mask)

    def post_step(self):
        pass

    def _set_pm_collision_type(self):
        pass


def trigger_triggers_triggered(arbiter, space, data):

    playground = data['playground']
    (trigger, _), (triggered, _) = get_colliding_entities(playground, arbiter)

    trigger.trigger()
    triggered.trigger()

    return True
