"""
Body Parts of an Agent.
"""

import os
from abc import ABC, abstractmethod

import yaml

from simple_playgrounds.entities.entity import Entity
from simple_playgrounds.utils.definitions import ActionTypes, CollisionTypes, Action

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

    @staticmethod
    def _parse_configuration(part_type):
        """
        Method to parse yaml configuration file.

        Args:
            part_type (str): Can be 'platform', 'eye', 'head', 'arm', 'hand'

        Returns:
            Dictionary containing the default configuration of the body part.

        """

        fname = 'parts_default.yml'

        __location__ = os.path.realpath(os.path.join(os.getcwd(), os.path.dirname(__file__)))
        with open(os.path.join(__location__, fname), 'r') as yaml_file:
            default_config = yaml.load(yaml_file, Loader=yaml.FullLoader)

        return default_config[part_type]

    @abstractmethod
    def get_available_actions(self):
        """
        Method that create a :obj: 'list' of :obj: 'Action'.
        An :obj:'Action' is a namedtuple (see Action in the definitions)

        Returns:
            List of available actions :obj: 'list' of :obj: 'Action'.

        """
        actions = []

        if self.can_grasp:
            actions.append(Action(self.name, ActionTypes.GRASP, ActionTypes.DISCRETE, 0, 1))

        if self.can_activate:
            actions.append(Action(self.name, ActionTypes.ACTIVATE, ActionTypes.DISCRETE, 0, 1))

        if self.can_eat:
            actions.append(Action(self.name, ActionTypes.EAT, ActionTypes.DISCRETE, 0, 1))

        return actions

    @abstractmethod
    def apply_actions(self, actions):
        """
        Apply the actions to the physical body part

        Args:
            actions (:obj: 'dict'): dictionary of actions. keys are ActionTypes, values are floats.

        """

        if self.can_activate:
            self.is_activating = actions.get(ActionTypes.ACTIVATE, False)

        if self.can_eat:
            self.is_eating = actions.get(ActionTypes.EAT, False)

        if self.can_grasp:
            self.is_grasping = actions.get(ActionTypes.GRASP, False)

        if self.is_holding and not self.is_grasping:
            self.is_holding = False

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
