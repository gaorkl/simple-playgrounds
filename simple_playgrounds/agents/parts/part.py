"""
Module that defines the Base Class for Body Parts of an Agent.

"""

import os
from abc import ABC, abstractmethod
import numbers

import yaml

from simple_playgrounds.entity import Entity
from simple_playgrounds.utils.definitions import ActionTypes, CollisionTypes

# pylint: disable=line-too-long


class Part(Entity, ABC):
    """
    Base class for Body Parts.
    Part inherits from Entity. It is a visible, movable Entity.

    """

    # pylint: disable=too-many-instance-attributes

    entity_type = 'part'
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

        Entity.__init__(self, initial_position=[0, 0, 0], visible=True, movable=True, **kwargs)
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
            self.grasp_actuator = Actuator(self.name, ActionTypes.GRASP, ActionTypes.DISCRETE, 0, 1)
            self.actuators.append(self.grasp_actuator)

        if self.can_activate:
            self.activate_actuator = Actuator(self.name, ActionTypes.ACTIVATE, ActionTypes.DISCRETE, 0, 1)
            self.actuators.append(self.activate_actuator)

        if self.can_eat:
            self.eat_actuator = Actuator(self.name, ActionTypes.EAT, ActionTypes.DISCRETE, 0, 1)
            self.actuators.append(self.eat_actuator)

    @staticmethod
    def _parse_configuration(part_type):
        """
        Method to parse yaml configuration file.

        Args:
            part_type (str): Can be 'platform', 'eye', 'head', 'arm', 'hand'

        Returns:
            Dictionary containing the default configuration of the body part.

        """

        file_name = 'utils/configs/agent_parts.yml'

        __location__ = os.path.dirname(os.path.dirname(os.path.realpath(os.path.join(os.getcwd(),
                                                                                     os.path.dirname(__file__)))))
        with open(os.path.join(__location__, file_name), 'r') as yaml_file:
            default_config = yaml.load(yaml_file, Loader=yaml.FullLoader)

        return default_config[part_type]

    def apply_action(self, actuator, value):
        """
        Apply the action to the physical body part.

        Args:
            actuator (:obj: 'Actuator'): Actuator on which action is applied.
            value (float): value of the Actuator

        """
        value = self._check_value_actuator(actuator, value)

        if self.can_activate and actuator is self.activate_actuator:
            self.is_activating = value

        if self.can_eat and actuator is self.eat_actuator:
            self.is_eating = value

        if self.can_grasp and actuator is self.grasp_actuator:
            self.is_grasping = value

        if self.is_holding and not self.is_grasping:
            self.is_holding = False

    @staticmethod
    def _check_value_actuator(actuator, value):

        if not isinstance(value, numbers.Real):
            raise ValueError('Action value for actuator ' + actuator.part_name + 'not a number')

        value = min(max(value, actuator.min), actuator.max)
        return value

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

    def __init__(self, part_name, action_type, action_range, min_value, max_value):
        """

        Args:
            part_name (str): name of the part that the Actuator is associated with.
            action_type: Type of action (change of angular velocity, grasp, ...). Defined using ActionTypes.
            action_range: Defines the range of actions (discrete, continuous centered). Defined using ActionTypes.
            min_value: Min action value
            max_value: Max action value
        """

        self.part_name = part_name

        self.action = action_type
        self.action_range = action_range

        self.min = min_value
        self.max = max_value

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
