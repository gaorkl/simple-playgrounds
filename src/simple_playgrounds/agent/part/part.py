""" Module that defines the base class Part and Actuator.

Part inherits from Entity, and is used to create different body parts
of an agent. Parts are visible and movable by default.

Examples on how to add Parts to an agent can be found
in simple_playgrounds/agents/agents.py
"""
from __future__ import annotations
from collections import namedtuple

import math
from abc import ABC, abstractmethod
from enum import IntEnum, auto
from typing import Tuple, TYPE_CHECKING, Optional, List, Union, Dict

from numpy.lib.function_base import iterable

from simple_playgrounds.entity.embodied.interactive import InteractiveEntity

if TYPE_CHECKING:
    from simple_playgrounds.agent.agent import Agent
    from simple_playgrounds.entity.embodied.embodied import EmbodiedEntity

import pymunk

from simple_playgrounds.common.definitions import ARM_MAX_FORCE, CollisionTypes
from simple_playgrounds.entity.embodied.physical import PhysicalEntity


# pylint: disable=line-too-long

if TYPE_CHECKING:
    _Base = EmbodiedEntity
else:
    _Base = object

DiscreteCommand = namedtuple('DiscreteCommand', ['n'])
ContinuousCommand = namedtuple('ContinuousCommand', ['min', 'max'])

Command = Union[DiscreteCommand, ContinuousCommand]
CommandDict = Dict[Command, Union[float, int]]

GaussianNoise = namedtuple()

class Part(_Base):
    """
    Mixin for Embodied entities that transform them into 
    actuated entities, that are controllable. 
    """

    # pylint: disable=too-many-instance-attributes

    def __init__(self, **_):
        self._agent: Optional[Agent] = None
        self._command_space: List[Command] = None

    @property
    def agent(self):
        return self._agent

    @agent.setter
    def agent(self, agent):
        self._agent = agent

    def reset(self):
        pass

    def pre_step(self, **kwargs):
        self._receive_commands(**kwargs)
        self._apply_commands()
        

    @abstractmethod
    def _apply_actions(self, **kwargs):
        ...

    @property
    def action_space(self):
        if not self._action_space:
            raise ValueError("Action Space should be set")
        return self._action_space


class PhysicalPart(Part, PhysicalEntity, ABC):

    def _set_pm_collision_type(self):
        self._pm_shape.collision_type = CollisionTypes.PART


class InteractivePart(Part, InteractiveEntity, ABC):

    def _set_pm_collision_type(self):
        self._pm_shape.collision_type = CollisionTypes.PART
