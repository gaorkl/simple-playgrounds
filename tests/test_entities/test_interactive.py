from simple_playgrounds.playground.playground import EmptyPlayground
from simple_playgrounds.common.definitions import CollisionTypes


from tests.mock_entities import MockPhysicalInteractive, trigger_triggers_triggered


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

# def test_interactive_vertices(self):

    # test that vertices are concave

    # test that vertices follow 

# def test_halo_halo_in_range(radius, interaction_radius):

#     playground = EmptyPlayground()
#     playground.add_interaction(CollisionTypes.TEST_TRIGGER, CollisionTypes.TEST_TRIGGERED, trigger_triggers_triggered)

#     contour = Contour(shape='circle', radius=radius)

#     ent_1 = MockPhysical(playground, ((0, 0), 0), contour=contour, movable=True, mass=5)
#     halo_1 = MockHaloTrigger(ent_1, interaction_range=interaction_radius, texture=(2, 3, 4))

#     ent_2 = MockPhysical(playground, ((0, 2*radius + 2*interaction_radius - 1), 0), contour=contour)
#     halo_2 = MockHaloTriggered(ent_2, interaction_range=interaction_radius, texture=(2, 3, 4))

#     assert not halo_1.activated and not halo_2.activated

#     playground.step()

#     assert halo_1.activated and halo_2.activated


# def test_halo_halo_out_range(radius, interaction_radius):

#     playground = EmptyPlayground()
#     playground.add_interaction(CollisionTypes.TEST_TRIGGER, CollisionTypes.TEST_TRIGGERED, trigger_triggers_triggered)

#     contour = Contour(shape='circle', radius=radius)

#     ent_1 = MockPhysical(playground, ((0, 0), 0), contour=contour, movable=True, mass=5)
#     halo_1 = MockHaloTrigger(ent_1, interaction_range=interaction_radius, texture=(2, 3, 4))

#     ent_2 = MockPhysical(playground, ((0, 2*radius + 2*interaction_radius + 1), 0), contour=contour)
#     halo_2 = MockHaloTriggered(anchor=ent_2, interaction_range=interaction_radius, texture=(2, 3, 4))

#     assert not halo_1.activated and not halo_2.activated

#     playground.step()

#     assert not halo_1.activated and not halo_2.activated


# def test_halo_standalone(radius, interaction_radius):

#     playground = EmptyPlayground()
#     playground.add_interaction(CollisionTypes.TEST_TRIGGER, CollisionTypes.TEST_TRIGGERED, trigger_triggers_triggered)


#     contour = Contour(shape='circle', radius=radius)

#     ent_1 = MockPhysical(playground, ((0, 0), 0), contour=contour, movable=True, mass=5)
#     halo_1 = MockHaloTrigger(ent_1, interaction_range=interaction_radius, texture=(2, 3, 4))

#     contour = Contour(shape='square', radius=radius)
#     zone = MockZoneTriggered(playground, ((0, 2*radius + interaction_radius - 1), 0), **contour.dict_attributes)

#     assert not halo_1.activated and not zone.activated

#     playground.step()

#     assert halo_1.activated and zone.activated
#     assert halo_1.position == (0, 0)
#     assert zone.position == (0, 2*radius + interaction_radius - 1)


# def test_standalone_standalone():

#     playground = EmptyPlayground()
#     playground.add_interaction(CollisionTypes.TEST_TRIGGER, CollisionTypes.TEST_TRIGGERED, trigger_triggers_triggered)

#     contour = Contour(shape='circle', radius=10)
#     zone_1 = MockZoneTrigger(playground, ((0, 5), 0), **contour.dict_attributes)
#     zone_2 = MockZoneTriggered(playground, ((0, -5), 0), **contour.dict_attributes)

#     assert not zone_1.activated and not zone_2.activated

#     playground.step()

#     # static objects don't generate collisions
#     assert not zone_1.activated and not zone_2.activated
