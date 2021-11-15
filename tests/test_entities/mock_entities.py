from typing import Optional

import pymunk

from simple_playgrounds.common.position_utils import Coordinate, InitCoord
from simple_playgrounds.entity.interactive import StandAloneInteractive, AnchoredInteractive
from simple_playgrounds.entity.physical import PhysicalEntity
from simple_playgrounds.common.definitions import CollisionTypes, PymunkCollisionCategories
from simple_playgrounds.playground.collision_handlers import get_colliding_entities


class MockPhysical(PhysicalEntity):

    def __init__(self, **kwargs):

        super().__init__(texture = (10, 10, 10), **kwargs)

    def move_to_position(self,
                         coordinates: Optional[Coordinate] = None,
                         **kwargs):
        self._move_to(coordinates)

    def update(self):
        pass


class MockHaloTrigger(AnchoredInteractive):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.activated = False

    def move_to_position(self,
                         coordinates: Optional[Coordinate] = None,
                         **kwargs):
        pass

    def pre_step(self):
        self.activated = False

    def update(self):
        pass

    def reset(self):
        pass

    def _set_pm_collision_type(self):
        self._pm_interactive_shape.collision_type = CollisionTypes.TEST_TRIGGER

    def trigger(self):
        self.activated = True


class MockHaloTriggered(MockHaloTrigger):

    def _set_pm_collision_type(self):
        self._pm_interactive_shape.collision_type = CollisionTypes.TEST_TRIGGERED


class MockZoneTrigger(StandAloneInteractive):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.activated = False

    def _set_pm_collision_type(self):
        self._pm_interactive_shape.collision_type = CollisionTypes.TEST_TRIGGER

    def move_to_position(self, coordinates: Optional[Coordinate] = None,
                         **kwargs):
        self._move_to(coordinates)

    def pre_step(self):
        self.activated = False

    def update(self):
        pass

    def reset(self):
        pass

    def trigger(self):
        self.activated = True


class MockZoneTriggered(MockZoneTrigger):

    def _set_pm_collision_type(self):
        self._pm_interactive_shape.collision_type = CollisionTypes.TEST_TRIGGERED


class MockBarrier(PhysicalEntity):

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

    def move_to_position(self, coordinates: Optional[InitCoord] = None, allow_overlapping: Optional[bool] = True,
                         max_attempts: Optional[int] = 100):
        self._move_to(coordinates)

    def update(self):
        pass


def trigger_triggers_triggered(arbiter, space, data):

    playground = data['playground']
    (trigger, _), (triggered, _) = get_colliding_entities(playground, arbiter)

    trigger.trigger()
    triggered.trigger()

    return True
