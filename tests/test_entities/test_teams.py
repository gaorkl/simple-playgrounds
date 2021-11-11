from typing import Optional

import numpy as np

from simple_playgrounds.playground.collision_handlers import get_colliding_entities

from simple_playgrounds.common.position_utils import Coordinate
from simple_playgrounds.common.contour import Contour
from simple_playgrounds.playground.playground import EmptyPlayground
from simple_playgrounds.entity import StandAloneInteractive, AnchoredInteractive

# Add test Interactions to collisions
from simple_playgrounds.common.definitions import CollisionTypes


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

    def _set_pm_collision_handler(self):
        self._pm_interactive_shape.collision_type = CollisionTypes.TEST_TRIGGER

    def trigger(self):
        self.activated = True


class MockHaloTriggered(MockHaloTrigger):

    def _set_pm_collision_handler(self):
        self._pm_interactive_shape.collision_type = CollisionTypes.TEST_TRIGGERED


class MockZoneTrigger(StandAloneInteractive):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.activated = False

    def _set_pm_collision_handler(self):
        self._pm_interactive_shape.collision_type = CollisionTypes.TEST_TRIGGER

    def move_to_position(self, coordinates: Optional[Coordinate] = None,
                         **kwargs):
        self.coordinates = coordinates

    def pre_step(self):
        self.activated = False

    def update(self):
        pass

    def reset(self):
        pass

    def trigger(self):
        self.activated = True


class MockZoneTriggered(MockZoneTrigger):

    def _set_pm_collision_handler(self):
        self._pm_interactive_shape.collision_type = CollisionTypes.TEST_TRIGGERED


def trigger_triggers_triggered(arbiter, space, data):

    playground = data['playground']
    (trigger, _), (triggered, _) = get_colliding_entities(playground, arbiter)

    trigger.trigger()
    triggered.trigger()

    return True


def test_same_team(physical_basic):

    playground = EmptyPlayground()
    playground.add_interaction(CollisionTypes.TEST_TRIGGER, CollisionTypes.TEST_TRIGGERED, trigger_triggers_triggered)

    halo = MockHaloTrigger(anchor=physical_basic, interaction_range=5, texture=(10, 10, 10))
    physical_basic.add_interactive(halo)
    physical_basic.add_to_team('team_1')

    playground.add(physical_basic, ((0, 0), 0))

    contour = Contour('square', 10, None, None)
    zone = MockZoneTriggered(**contour._asdict(), texture=(10, 10, 10))
    zone.add_to_team('team_1')

    playground.add(zone, ((0, 0), 0))

    playground.update()

    assert halo.activated and zone.activated


def test_different_team(physical_basic):

    playground = EmptyPlayground()
    playground.add_interaction(CollisionTypes.TEST_TRIGGER, CollisionTypes.TEST_TRIGGERED, trigger_triggers_triggered)

    halo = MockHaloTrigger(anchor=physical_basic, interaction_range=5, texture=(10, 10, 10))
    physical_basic.add_interactive(halo)
    physical_basic.add_to_team('team_1')

    playground.add(physical_basic, ((0, 0), 0))

    contour = Contour('square', 10, None, None)
    zone = MockZoneTriggered(**contour._asdict(), texture=(10, 10, 10))
    zone.add_to_team('team_2')

    playground.add(zone, ((0, 0), 0))

    playground.update()

    assert not halo.activated and not zone.activated


def test_multiple_teams(physical_basic):

    playground = EmptyPlayground()
    playground.add_interaction(CollisionTypes.TEST_TRIGGER, CollisionTypes.TEST_TRIGGERED, trigger_triggers_triggered)

    halo = MockHaloTrigger(anchor=physical_basic, interaction_range=5, texture=(10, 10, 10))
    physical_basic.add_interactive(halo)
    physical_basic.add_to_team('team_1')
    physical_basic.add_to_team('team_2')

    playground.add(physical_basic, ((0, 0), 0))

    # adding a team after entering playground should also work.
    physical_basic.add_to_team('team_3')

    contour = Contour('square', 10, None, None)
    zone_1 = MockZoneTriggered(**contour._asdict(), texture=(10, 10, 10))
    zone_1.add_to_team('team_2')
    zone_1.add_to_team('team_4')

    playground.add(zone_1, ((0, 0), 0))

    playground.update()

    assert halo.activated and zone_1.activated


def test_multiple_triggered(physical_basic):

    playground = EmptyPlayground()
    playground.add_interaction(CollisionTypes.TEST_TRIGGER, CollisionTypes.TEST_TRIGGERED, trigger_triggers_triggered)

    halo = MockHaloTrigger(anchor=physical_basic, interaction_range=5, texture=(10, 10, 10))
    physical_basic.add_interactive(halo)
    physical_basic.add_to_team('team_1')

    playground.add(physical_basic, ((0, 0), 0))

    contour = Contour('square', 10, None, None)
    zone_1 = MockZoneTriggered(**contour._asdict(), texture=(10, 10, 10))
    zone_1.add_to_team('team_1')

    playground.add(zone_1, ((0, 0), 0))

    zone_2 = MockZoneTriggered(**contour._asdict(), texture=(10, 10, 10))
    zone_2.add_to_team('team_1')

    playground.add(zone_2, ((0, 0), 0))

    zone_3 = MockZoneTriggered(**contour._asdict(), texture=(10, 10, 10))
    zone_3.add_to_team('team_2')

    playground.add(zone_3, ((0, 0), 0))

    playground.update()

    assert halo.activated and zone_1.activated and zone_2.activated
    assert not zone_3.activated
    # assert not zone_2.activated





