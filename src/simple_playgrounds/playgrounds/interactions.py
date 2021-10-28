from __future__ import annotations
from typing import Tuple, Union, List, Dict, Optional, Type, TYPE_CHECKING
if TYPE_CHECKING:
    from simple_playgrounds.playgrounds.playground import Playground

import pymunk

from simple_playgrounds.elements.element import InteractiveElement, SceneElement
from simple_playgrounds.elements.collection.gem import GemElement
from simple_playgrounds.elements.collection.teleport import TeleportElement
from simple_playgrounds.elements.collection.modifier import ModifierElement

from simple_playgrounds.agents.agent import Agent, Part
from simple_playgrounds.agents.parts.actuators import Grasp, Activate

from simple_playgrounds.common.devices import Device


def get_interaction_participants(playground: Playground, arbiter)


# Collision Handlers


def _agent_touches_element(playground: Playground,
                           arbiter: pymunk.Arbiter,
                           space, data):

    agent: Agent = playground.get_entity_from_shape(arbiter.shapes[0])
    touched_element = playground.get_entity_from_shape(arbiter.shapes[1])

    if not touched_element:
        return True

    assert isinstance(touched_element, InteractiveElement)

    agent.reward += touched_element.reward

    elems_remove, elems_add = touched_element.activate(agent)
    playground.remove_add_within(elems_remove, elems_add)

    if touched_element.terminate_upon_activation:
        playground.done = True

    return True

def _agent_activates_element(playground: Playground, arbiter, space, data):

    agent: Agent = playground.get_entity_from_shape(arbiter.shapes[0])
    part: Part = agent.get_part_from_shape(arbiter.shapes[0])
    activable_element = playground.get_entity_from_shape(arbiter.shapes[1])

    if not activable_element:
        return True

    assert isinstance(activable_element, InteractiveElement)

    # Note: later, should handle the case where two agents activate simultaneously.
    for actuator in agent.actuators:
        if actuator.part is part and isinstance(actuator, Activate):

            if actuator.is_activating and not activable_element.activated:

                agent.reward += activable_element.reward

                elems_remove, elems_add = activable_element.activate(agent)
                playground.remove_add_within(elems_remove, elems_add)

                if activable_element.terminate_upon_activation:
                    playground.done = True

                actuator.is_activating = False

    return True


def _agent_grasps_element(playground: Playground, arbiter, space, data):

    agent: Agent = playground.get_entity_from_shape(arbiter.shapes[0])
    part: Part = agent.get_part_from_shape(arbiter.shapes[0])
    grasped_element = playground.get_entity_from_shape(arbiter.shapes[1])

    if not grasped_element:
        return True

    assert isinstance(grasped_element, SceneElement)

    for actuator in agent.actuators:

        if actuator.part is part and isinstance(actuator, Grasp):

            if actuator.is_grasping and not actuator.is_holding:

                actuator.is_holding = grasped_element

                j_1 = pymunk.PinJoint(part.pm_body,
                                      grasped_element.pm_body, (0, 0),
                                      (0, 20))
                j_2 = pymunk.PinJoint(part.pm_body,
                                      grasped_element.pm_body, (0, 0),
                                      (0, -20))

                j_3 = pymunk.PinJoint(part.pm_body,
                                      grasped_element.pm_body, (0, 20),
                                      (0, 0))
                j_4 = pymunk.PinJoint(part.pm_body,
                                      grasped_element.pm_body, (0, -20),
                                      (0, 0))

                playground._space.add(j_1, j_2, j_3, j_4)
                actuator.grasped = [j_1, j_2, j_3, j_4]

                playground._grasped_elements[grasped_element] = actuator

    return True

def _gem_activates_element(playground: Playground, arbiter, space, data):

    gem = playground.get_entity_from_shape(arbiter.shapes[0])
    activable_element = playground.get_entity_from_shape(arbiter.shapes[1])

    assert isinstance(activable_element, InteractiveElement)

    agent = playground._get_closest_agent(gem)

    if not gem:
        return True

    assert isinstance(gem, GemElement)

    if not activable_element.activated:

        elems_remove, elems_add = activable_element.activate(gem)
        playground.remove_add_within(elems_remove, elems_add)

        agent.reward += activable_element.reward

        if activable_element.terminate_upon_activation:
            playground.done = True

    return True

def _agent_teleports(playground, arbiter, space, data):

    agent = playground._get_agent_from_shape(arbiter.shapes[0])
    teleport = playground._get_element_from_shape(arbiter.shapes[1])

    assert isinstance(teleport, TeleportElement)

    if ((agent, teleport) in playground._teleported) or agent.is_teleporting:
        return True

    if isinstance(teleport.destination, TeleportElement):
        playground._teleported.append((agent, teleport.destination))

    new_position, new_angle = teleport.energize(agent)

    delta_angle = agent.angle - new_angle

    agent.position, agent.angle = new_position, new_angle

    if teleport.keep_inertia:
        agent.velocity = pymunk.Vec2d(
            *agent.velocity).rotated(-delta_angle)
    else:
        agent.velocity = (0, 0)

    agent.is_teleporting = True

    return True

def _modifier_modifies_device(playground, arbiter, space, data):

    modifier = playground._get_element_from_shape(arbiter.shapes[0])
    device = playground._get_device_from_shape(arbiter.shapes[1])

    assert isinstance(device, Device)
    assert isinstance(modifier, ModifierElement)

    modifier.modify(device)

    return True