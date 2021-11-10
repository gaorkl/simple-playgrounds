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


def test_halo_halo(physical_basic, physical_basic_2):

    playground = EmptyPlayground()
    playground.add_interaction(CollisionTypes.TEST_TRIGGER, CollisionTypes.TEST_TRIGGERED, trigger_triggers_triggered)

    halo_1 = MockHaloTrigger(anchor=physical_basic, interaction_range=5, texture=(2,3,4))
    physical_basic.add_interactive(halo_1)

    playground.add(physical_basic, ((0, 0), 0))

    playground.add(physical_basic_2, ((physical_basic.contour.radius + physical_basic_2.contour.radius + 7, 0), 0))

    halo_2 = MockHaloTriggered(anchor=physical_basic_2, interaction_range=5, texture=(2, 3, 4))
    physical_basic_2.add_interactive(halo_2)

    assert not halo_1.activated and not halo_2.activated

    playground.update()

    assert halo_1.activated and halo_2.activated


def test_halo_halo_outrange(physical_basic, physical_basic_2):
    playground = EmptyPlayground()
    playground.add_interaction(CollisionTypes.TEST_TRIGGER, CollisionTypes.TEST_TRIGGERED, trigger_triggers_triggered)

    halo_1 = MockHaloTrigger(anchor=physical_basic, interaction_range=5, texture=(2, 3, 4))
    physical_basic.add_interactive(halo_1)

    playground.add(physical_basic, ((0, 0), 0))

    playground.add(physical_basic_2, ((physical_basic.contour.radius + physical_basic_2.contour.radius + 11, 0), 0))

    halo_2 = MockHaloTriggered(anchor=physical_basic_2, interaction_range=5, texture=(2, 3, 4))
    physical_basic_2.add_interactive(halo_2)

    assert not halo_1.activated and not halo_2.activated

    playground.update()

    assert not halo_1.activated and not halo_2.activated


def test_halo_standalone(physical_basic):

    playground = EmptyPlayground()
    playground.add_interaction(CollisionTypes.TEST_TRIGGER, CollisionTypes.TEST_TRIGGERED, trigger_triggers_triggered)

    halo_1 = MockHaloTrigger(anchor=physical_basic, interaction_range=5, texture = (10, 10, 10))
    physical_basic.add_interactive(halo_1)

    playground.add(physical_basic, ((0, 0), 0))

    contour = Contour('square', 10, None, None)
    zone = MockZoneTriggered(**contour._asdict(), texture = (10, 10, 10))

    playground.add(zone, ((0, 0), 0))

    assert not halo_1.activated and not zone.activated

    playground.update()

    assert halo_1.activated and zone.activated
    assert halo_1.position == zone.position





