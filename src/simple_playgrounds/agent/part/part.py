""" Module that defines the base class Part and Actuator.

Part inherits from Entity, and is used to create different body parts
of an agent. Parts are visible and movable by default.

Examples on how to add Parts to an agent can be found
in simple_playgrounds/agents/agents.py
"""
from __future__ import annotations
from abc import ABC, abstractmethod
from collections import namedtuple
from typing import Dict, Optional, TYPE_CHECKING, Tuple, Union, List

import pymunk

from simple_playgrounds.common.definitions import CollisionTypes
from simple_playgrounds.entity.embodied.physical import PhysicalEntity

if TYPE_CHECKING:
    from simple_playgrounds.agent.agent import Agent
    from simple_playgrounds.entity.embodied.embodied import EmbodiedEntity
    _Base = EmbodiedEntity
else:
    _Base = object

DiscreteCommand = namedtuple('DiscreteCommand', ['n'])
ContinuousCommand = namedtuple('ContinuousCommand', ['min', 'max'])

Command = Union[DiscreteCommand, ContinuousCommand]
CommandDict = Dict[Command, Union[float, int]]


class Part(_Base):
    """
    Mixin to transform an embodied entity into a Part.
    Parts can be controlled, and sensors can be attached to them.
    """
    
    def __init__(self, 
                 anchor: Optional[Union[Agent, PhysicalPart]] = None,
                 **kwargs):

        if isinstance(anchor, Agent):
            self._agent = anchor
        elif isinstance(anchor, PhysicalPart):
            self._agent = anchor.agent
        else:
            self._agent = self

        if anchor:
            self._anchor = anchor
        else:
            self._anchor = self

        # Add physical motors if needed
        self._commands: List[Command] = self._set_commands(**kwargs)
        self._command_values: CommandDict = self.null_commands
    
    @property
    def anchor(self):
        return self._anchor
    
    @property
    def agent(self):
        return self._agent

    @property
    def rng(self):
        return self._anchor.rng

    @abstractmethod
    def _set_commands(self, **kwargs) -> List[Command]:
        ...

    @property
    @abstractmethod
    def commands(self):
        return self._commands

    @property
    def null_commands(self) -> CommandDict:
        return {command: 0 for command in self._commands}

    @property
    def random_commands(self) -> CommandDict:
        assert self._rng
        commands = {}
        for command in self._commands:
            if isinstance(command, DiscreteCommand):
                commands[command] = self._rng.integers(0, command.n, 
                                                       endpoint=True)
            elif isinstance(command, ContinuousCommand):
                commands[command] = self._rng.uniform(command.min, command.max)

        return commands


class PhysicalPart(Part, PhysicalEntity, ABC):
    
    def __init__(self, **kwargs):

        Part.__init__(**kwargs)

        if self._anchor:
            # Move to position, then attach
            self._set_relative_coordinates(**kwargs)
            self._anchor_point, self._part_point, self._angle_offset = self._attach_to_anchor(**kwargs)
    
    def _attach_to_anchor(self,
                          anchor_point: Union[pymunk.Vec2d, Tuple[float, float]],
                          part_point: Union[pymunk.Vec2d, Tuple[float, float]],
                          rotation_range: float,
                          angle_offset: float = 0):

        assert self._anchor

        # convert to point 2d
        anchor_point = pymunk.Vec2d(*anchor_point)
        part_point = pymunk.Vec2d(*part_point)

        # Create joint to attach to anchor
        self._joint = pymunk.PivotJoint(self._anchor.pm_body, self.pm_body,
                                       anchor_point, part_point)  
        self._joint.collide_bodies = False
        self._limit = pymunk.RotaryLimitJoint(
            self._anchor.pm_body, self._pm_body,
            angle_offset - rotation_range / 2,
            angle_offset + rotation_range / 2)

        self._motor = pymunk.SimpleMotor(self._anchor.pm_body, self.pm_body, 0)

        return anchor_point, part_point, angle_offset
        
    def _set_relative_coordinates(self):
        """
        Calculates the position of a Part relative to its Anchor.
        Sets the position of the Part.
        """

        assert self._anchor
        self._pm_body.position = self._anchor.position\
            + self._anchor_point.rotated(self._anchor.angle)\
            - self._part_point.rotated(
                self._anchor.angle + self._angle_offset)
       
        self._pm_body.angle = self._anchor.pm_body.angle + self._angle_offset

    def reset(self):
        pass

    def pre_step(self, **kwargs):
        self._check_commands(**kwargs)
        self._apply_noise(**kwargs)
        self._update_actuators(**kwargs)

    @abstractmethod
    def _check_commands(self, 
                        commands: CommandDict,
                        hard_check: Optional[bool] = True):
        """
        Filter commands that belong to the agent.
        Check that commands are in the correct space.
        If not, convert them, or raise an Error.
        """
        ...

    @abstractmethod
    def _apply_noise(self, **kwargs):
        ...

    @abstractmethod
    def _update_actuators(self, **kwargs):
        ...
    def reindex_shapes(self):
        assert self._playground
        self._playground.space.reindex_shapes_for_body(self._pm_body)

    def _set_pm_collision_type(self):
        self._pm_shape.collision_type = CollisionTypes.PART


# class InteractivePart(PartMixin, InteractiveEntity, ABC):

#     def _set_pm_collision_type(self):
#         self._pm_shape.collision_type = CollisionTypes.PART
