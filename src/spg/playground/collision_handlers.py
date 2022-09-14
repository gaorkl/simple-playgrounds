from __future__ import annotations

from typing import TYPE_CHECKING

from ..agent.interactor import Grasper
from ..agent.part import PhysicalPart

if TYPE_CHECKING:
    from .playground import Playground


def get_colliding_entities(playground: Playground, arbiter):

    entity_1 = playground.get_entity_from_shape(arbiter.shapes[0])
    entity_2 = playground.get_entity_from_shape(arbiter.shapes[1])

    agent_1 = None
    agent_2 = None

    if isinstance(entity_1, PhysicalPart):
        agent_1 = entity_1.agent

    if isinstance(entity_2, PhysicalPart):
        agent_2 = entity_2.agent

    return (entity_1, agent_1), (entity_2, agent_2)


# Collision Handlers


def grasper_grasps_graspable(arbiter, _, data):

    playground: Playground = data["playground"]
    (grasper, _), (entity, _) = get_colliding_entities(playground, arbiter)

    assert isinstance(grasper, Grasper)

    if grasper.start_grasping:
        grasper.grasp(entity)

    return True


# def agent_touches_element(arbiter, space, data):

#     playground: Playground = data['playground']
#     (part, agent), (touched_element, _) = get_colliding_entities(playground, arbiter)

#     if not touched_element:
#         return True

#     assert isinstance(touched_element, InteractiveElement)
#     assert isinstance(agent, Agent)

#     agent.reward += touched_element.reward

#     elems_remove, elems_add = touched_element.activate(agent)
#     playground.remove_add_within(elems_remove, elems_add)

#     if touched_element.terminate_upon_activation:
#         playground.done = True

#     return True


# def agent_activates_element(arbiter, space, data):

#     playground: Playground = data['playground']
#     (part, agent), (activable_element, _) =
# get_colliding_entities(playground, arbiter)

#     if not activable_element:
#         return True

#     assert isinstance(activable_element, InteractiveElement)
# def grasper_grasps_graspable(arbiter, space, data)
#     assert isinstance(agent, Agent)

#     # Note: later, should handle the case where two agents activate simultaneously.
#     for actuator in agent.actuators:
#         if actuator.part is part and isinstance(actuator, Activate):

#             if actuator.is_activating and not activable_element.activated:

#                 agent.reward += activable_element.reward

#                 elems_remove, elems_add = activable_element.activate(agent)
#                 playground.remove_add_within(elems_remove, elems_add)

#                 if activable_element.terminate_upon_activation:
#                     playground.done = True

#                 actuator.is_activating = False

#     return True


# def gem_activates_element(arbiter, space, data):

#     playground: Playground = data['playground']
#     (gem, _), (activable_element, _) = get_colliding_entities(playground, arbiter)

#     assert isinstance(activable_element, InteractiveElement)

#     agent = playground.get_closest_agent(gem)

#     if not gem:
#         return True

#     assert isinstance(gem, GemElement)

#     if not activable_element.activated:

#         elems_remove, elems_add = activable_element.activate(gem)
#         playground.remove_add_within(elems_remove, elems_add)

#         agent.reward += activable_element.reward

#         if activable_element.terminate_upon_activation:
#             playground.done = True

#     return True


# def agent_teleports(arbiter, space, data):

#     playground: Playground = data['playground']
#     (_, agent), (teleport, _) = get_colliding_entities(playground, arbiter)

#     assert isinstance(teleport, TeleportElement)

#     if agent.has_teleported:
#         return True

#     teleport.energize(agent)

#     return True


# def modifier_modifies_device(arbiter, space, data):

#     playground: Playground = data['playground']
#     (modifier, _), (device, _) = get_colliding_entities(playground, arbiter)

#     assert isinstance(device, Device)
#     assert isinstance(modifier, ModifierElement)

#     modifier.modify(device)

#     return True
