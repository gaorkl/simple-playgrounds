from simple_playgrounds.playground.playground import EmptyPlayground
from simple_playgrounds.common.definitions import CollisionTypes


from tests.mock_entities import MockHalo, MockPhysicalInteractive, trigger_triggers_triggered, NonConvexC, MockZoneInteractive, MockPhysicalTrigger


coord_center = (0, 0), 0

def test_trigger():

    playground = EmptyPlayground()
    playground.add_interaction(CollisionTypes.TEST_TRIGGER, CollisionTypes.TEST_TRIGGERED, trigger_triggers_triggered)

    center_0 = (0, 0), 0
    trigger_1 = MockPhysicalInteractive(playground, center_0, radius = 10, interaction_range=5, trigger = True)

    center_1 = (0, 25), 0
    triggered_1 = MockPhysicalInteractive(playground, center_1, radius = 10, interaction_range=5, triggered = True)

    center_2 = (0, 50), 0
    triggered_2 = MockPhysicalInteractive(playground, center_2, radius = 10, interaction_range=5, triggered = True)

    playground.step()

    # Assert activations are correct
    assert trigger_1.halo.activated
    assert triggered_1.halo.activated
    assert not triggered_2.halo.activated

    # Assert entities don't movable
    assert trigger_1.coordinates == center_0
    assert triggered_1.coordinates == center_1
    assert triggered_2.coordinates == center_2

def test_non_convex_entity():

    playground = EmptyPlayground()
    playground.add_interaction(CollisionTypes.TEST_TRIGGER, CollisionTypes.TEST_TRIGGERED, trigger_triggers_triggered)
    
    ent_1 = NonConvexC(playground, coord_center, 35, 10)
    halo_1 = MockHalo(ent_1, interaction_range=10, triggered=False, trigger = True)

    ent_2 = MockPhysicalInteractive(playground, coord_center, radius = 20, interaction_range=10, triggered = True)

    playground.step()

    assert ent_1.coordinates == coord_center
    assert ent_2.coordinates == coord_center

    assert halo_1.activated
    assert ent_2.halo.activated

def test_zone_triggers():
    
    playground = EmptyPlayground()
    playground.add_interaction(CollisionTypes.TEST_TRIGGER, CollisionTypes.TEST_TRIGGERED, trigger_triggers_triggered)
    
    zone_1 = MockZoneInteractive(playground, coord_center, 35, trigger=True)

    ent_2 = MockPhysicalInteractive(playground, coord_center, radius = 20, interaction_range=10, triggered = True)

    playground.step()

    assert zone_1.coordinates == coord_center
    assert ent_2.coordinates == coord_center

    assert zone_1.activated
    assert ent_2.halo.activated


def test_physical_triggers():
    
    playground = EmptyPlayground()
    playground.add_interaction(CollisionTypes.TEST_TRIGGER, CollisionTypes.TEST_TRIGGERED, trigger_triggers_triggered)
    
    zone_1 = MockZoneInteractive(playground, coord_center, 35, triggered=True)

    ent_2 = MockPhysicalTrigger(playground, coord_center, radius = 20)

    playground.step()

    assert zone_1.coordinates == coord_center
    assert ent_2.coordinates == coord_center

    assert zone_1.activated
    assert ent_2._activated





def test_trigger_same_team():

    playground = EmptyPlayground()
    playground.add_interaction(CollisionTypes.TEST_TRIGGER, CollisionTypes.TEST_TRIGGERED, trigger_triggers_triggered)

    center_0 = (0, 0), 0
    trigger_1 = MockPhysicalInteractive(playground, center_0, radius = 10, interaction_range=5, trigger = True, teams = 'team_0')

    center_1 = (0, 25), 0
    triggered_1 = MockPhysicalInteractive(playground, center_1, radius = 10, interaction_range=5, triggered = True, teams = 'team_0')

    playground.step()

    # Assert activations are correct
    assert trigger_1.halo.activated
    assert triggered_1.halo.activated

    # Assert entities don't movable
    assert trigger_1.coordinates == center_0
    assert triggered_1.coordinates == center_1



def test_trigger_different_team():

    playground = EmptyPlayground()
    playground.add_interaction(CollisionTypes.TEST_TRIGGER, CollisionTypes.TEST_TRIGGERED, trigger_triggers_triggered)

    center_0 = (0, 0), 0
    trigger_1 = MockPhysicalInteractive(playground, center_0, radius = 10, interaction_range=5, trigger = True, teams = 'team_0')

    center_1 = (0, 25), 0
    triggered_1 = MockPhysicalInteractive(playground, center_1, radius = 10, interaction_range=5, triggered = True, teams = 'team_1')

    playground.step()

    # Assert activations are correct
    assert not trigger_1.halo.activated
    assert not triggered_1.halo.activated

    # Assert entities don't movable
    assert trigger_1.coordinates == center_0
    assert triggered_1.coordinates == center_1



def test_trigger_common_team():

    playground = EmptyPlayground()
    playground.add_interaction(CollisionTypes.TEST_TRIGGER, CollisionTypes.TEST_TRIGGERED, trigger_triggers_triggered)

    center_0 = (0, 0), 0
    trigger_1 = MockPhysicalInteractive(playground, center_0, radius = 10, interaction_range=5, trigger = True, teams = ['team_0', 'team_1'])

    center_1 = (0, 25), 0
    triggered_1 = MockPhysicalInteractive(playground, center_1, radius = 10, interaction_range=5, triggered = True, teams = ['team_1', 'team_2'])

    playground.step()

    # Assert activations are correct
    assert trigger_1.halo.activated
    assert triggered_1.halo.activated

    # Assert entities don't movable
    assert trigger_1.coordinates == center_0
    assert triggered_1.coordinates == center_1



