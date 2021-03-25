""" Module that defines the base class Part.

Part inherits from Entity, and is used to create different body parts
of an agent. Parts are visible and movable by default.
Two different kind of body parts inherit from Part: Link and Platform.
Platform is the base of an Agent while Link is an additional part which
can be attached to Link or Platform.

Examples can be found in simple_playgrounds/agents/agents.py
"""

import numbers
from abc import ABC

import numpy as np
import pymunk

from simple_playgrounds.entity import Entity
from simple_playgrounds.utils.definitions import (ANGULAR_VELOCITY,
                                                  LINEAR_FORCE, ActionSpaces,
                                                  ActionTypes, AgentPartTypes,
                                                  CollisionTypes)

# pylint: disable=line-too-long


class Part(Entity, ABC):
    """
    Base class for Body Parts.
    Part inherits from Entity. It is a visible, movable Entity.

    """

    # pylint: disable=too-many-instance-attributes

    entity_type = AgentPartTypes.PART
    part_type = None
    movable = True
    background = False

    def __init__(self, **kwargs):
        """
        Args:
            **kwargs: Optional Keyword Arguments

        Keyword Args:
            can_absorb (:obj: 'bool'): Part can absorb absorbable entities on contact.
                Default: False.
            can_eat (:obj: 'bool'): Part can eat edible entities.
                Default: False.
            can_activate (:obj: 'bool'): Part can activate activable entities.
                Default: False.
            can_grasp (:obj: 'bool'): Part can grasp graspable entities.
                Default: False.

        Note:
            All physical properties of the Part can be set as keyword argument.
            Refer to the Entity class for the list of available keyword arguments.

        """

        Entity.__init__(self, visible=True, movable=True, **kwargs)
        self.pm_visible_shape.collision_type = CollisionTypes.AGENT

        self.can_absorb = kwargs.get('can_absorb', False)
        self.can_eat = kwargs.get('can_eat', False)
        self.can_activate = kwargs.get('can_activate', False)
        self.can_grasp = kwargs.get('can_grasp', False)
        self.grasped = []

        self.is_eating = False
        self.is_activating = False
        self.is_grasping = False
        self.is_holding = False

        self.actuators = []

        if self.can_grasp:
            self.grasp_actuator = Actuator(self.name, ActionTypes.GRASP, ActionSpaces.DISCRETE_BINARY)
            self.actuators.append(self.grasp_actuator)

        if self.can_activate:
            self.activate_actuator = Actuator(self.name, ActionTypes.ACTIVATE, ActionSpaces.DISCRETE_BINARY)
            self.actuators.append(self.activate_actuator)

        if self.can_eat:
            self.eat_actuator = Actuator(self.name, ActionTypes.EAT, ActionSpaces.DISCRETE_BINARY)
            self.actuators.append(self.eat_actuator)

    def apply_action(self, actuator, value):
        """
        Apply the action to the physical body part.

        Args:
            actuator (:obj: 'Actuator'): Actuator on which action is applied.
            value (float): value of the Actuator

        """
        actuator.action_cb(self, value)

    def reset(self):

        super().reset()

        if self.can_activate:
            self.is_activating = False
        if self.can_eat:
            self.is_eating = False
        if self.can_grasp:
            self.is_grasping = False
            self.grasped = []
            self.is_holding = False


class Actuator:

    """
    Actuator classes defines how one body acts.
    It is used to define physical movements as well as interactions (eat, grasp, ...)
    of parts of an agent.
    """

    def __init__(self, part_name, action_type, action_space, action_range=1):
        """

        Args:
            part_name (str): name of the part that the Actuator is associated with.
            action_type: Type of action (change of angular velocity, grasp, ...). Defined using ActionTypes.
            action_space: Defines the range of actions (discrete, continuous centered). Defined using ActionTypes.
            action_range: For continuous actions, multiplies action values by this factor.
        """

        self.part_name = part_name

        self.action_type = action_type
        self.action_space = action_space

        self.action_range = action_range

        self.has_key_mapping = False
        self.key_map = {}

    def assign_key(self, key, key_behavior, value):
        """
        Assign keyboard key to a value.

        Args:
            key: PyGame keyboard key.
            key_behavior: KeyTypes.PRESS_HOLD or KeyTypes.PRESS_ONCE
            value: value of the actuator when key is pressed.

        """

        self.has_key_mapping = True
        self.key_map[key] = [key_behavior, value]

    def _check_value(self, value):

        if not isinstance(value, numbers.Real):
            raise ValueError('Action value for actuator ' + self.part_name +
                             'not a number')

        if self.action_space == ActionSpaces.CONTINUOUS_CENTERED:
            assert -self.action_range <= value <= self.action_range

        elif self.action_space == ActionSpaces.CONTINUOUS_POSITIVE:
            assert 0.0 <= value <= self.action_range

        elif self.action_space == ActionSpaces.DISCRETE_BINARY:
            assert value in [0, 1]

        elif self.action_space == ActionSpaces.DISCRETE_CENTERED:
            assert value in [-1, 0, 1]

        elif self.action_space == ActionSpaces.DISCRETE_POSITIVE:
            assert value in [0, 1]

    @property
    def min(self):
        if self.action_space == ActionSpaces.CONTINUOUS_CENTERED:
            return -self.action_range

        elif self.action_space == ActionSpaces.CONTINUOUS_POSITIVE:
            return 0.0

        elif self.action_space == ActionSpaces.DISCRETE_BINARY:
            return 0

        elif self.action_space == ActionSpaces.DISCRETE_CENTERED:
            return -1

        elif self.action_space == ActionSpaces.DISCRETE_POSITIVE:
            return 0

    @property
    def max(self):
        if self.action_space == ActionSpaces.CONTINUOUS_CENTERED:
            return self.action_range

        elif self.action_space == ActionSpaces.CONTINUOUS_POSITIVE:
            return self.action_range

        elif self.action_space == ActionSpaces.DISCRETE_BINARY:
            return 1

        elif self.action_space == ActionSpaces.DISCRETE_CENTERED:
            return 1

        elif self.action_space == ActionSpaces.DISCRETE_POSITIVE:
            return 1

    def action_cb(self, part, value):
        self._check_value(value)

        if part.can_activate and self.action_type is ActionTypes.ACTIVATE:
            part.is_activating = value

        if part.can_eat and self.action_type is ActionTypes.EAT:
            self.is_eating = value

        if part.can_grasp and self.action_type is ActionTypes.GRASP:
            self.is_grasping = value

        if part.is_holding and not part.is_grasping:
            part.is_holding = False

        if self.action_type is ActionTypes.LONGITUDINAL_FORCE:
            part.pm_body.apply_force_at_local_point(
                pymunk.Vec2d(value, 0) * LINEAR_FORCE, (0, 0))

        if self.action_type is ActionTypes.LATERAL_FORCE:
            part.pm_body.apply_force_at_local_point(
                pymunk.Vec2d(0, -value) * LINEAR_FORCE, (0, 0))

        if self.action_type is ActionTypes.ANGULAR_VELOCITY:
            part.pm_body.angular_velocity = value * ANGULAR_VELOCITY

        if self.action_type is ActionTypes.LINK:
            # Case when theta close to limit -> speed to zero
            theta_part = part.angle
            theta_anchor = part.anchor.angle

            angle_centered = (theta_part - (theta_anchor + part._angle_offset))
            angle_centered = angle_centered % (2 * np.pi)
            angle_centered = (angle_centered - 2 * np.pi
                              if angle_centered > np.pi else angle_centered)

            # Do not set the motor if the limb is close to limit
            if (angle_centered <
                    -part._rotation_range / 2 + np.pi / 20) and value > 0:
                part.motor.rate = 0

            elif (angle_centered >
                  part._rotation_range / 2 - np.pi / 20) and value < 0:
                part.motor.rate = 0

            else:
                part.motor.rate = value * ANGULAR_VELOCITY
