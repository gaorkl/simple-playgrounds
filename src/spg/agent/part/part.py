""" Module that defines the base class Part and Actuator.

Part inherits from Entity, and is used to create different body parts
of an agent. Parts are visible and movable by default.

Examples on how to add Parts to an agent can be found
in spg/agents/agents.py
"""
from __future__ import annotations

import math
from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Dict, List, Optional, Union

import pymunk
from gymnasium import spaces

from ...entity import PhysicalEntity
from ...utils.definitions import CollisionTypes
from ..device import Device
from ..device.interactor.grasper import Grasper
from ..device.sensor import RaySensor

if TYPE_CHECKING:
    from ...utils.position import Coordinate
    from ..agent import Agent


class PhysicalPart(PhysicalEntity, ABC):
    def __init__(self, name, **kwargs):

        super().__init__(
            name=name,
            teams=None,
            **kwargs,
        )

        # Add physical motors if needed
        self._anchored: List[AnchoredPart] = []
        self._devices: Dict[str, Device] = {}

        self._agent: Optional[Agent] = None

        self.grasper: Optional[Grasper] = None

        self._disabled = False

    @property
    def agent(self):
        return self._agent

    @agent.setter
    def agent(self, agent: Agent):
        self._agent = agent

    @property
    def anchored(self):
        return self._anchored

    @property
    def devices(self):
        return self._devices

    @property
    def teams(self):
        return self._teams

    @teams.setter
    def teams(self, teams):
        self._teams = teams

    def add(
        self,
        elem: Union[AnchoredPart, Device],
        anchor_coordinates: Optional[Coordinate] = None,
    ):

        elem.anchor = self
        elem.teams = self._teams

        if isinstance(elem, AnchoredPart):

            assert elem.name not in self.agent.parts

            if anchor_coordinates:
                elem.anchor_coordinates = anchor_coordinates
            self._anchored.append(elem)

        elif isinstance(elem, Device):

            assert elem.name not in self._devices

            self._devices[elem.name] = elem

            if isinstance(elem, RaySensor) and self._playground:
                self.playground.sensor_shader.add(elem)

            elif isinstance(elem, Grasper):
                if self.grasper:
                    raise ValueError("Grasper already in. Only one grasper per part.")

                self.grasper = elem

        else:
            raise ValueError("Not implemented")

        if isinstance(elem, AnchoredPart):
            assert self._agent
            self._agent.add(elem)

    def move_to(  # pylint: disable=arguments-differ
        self,
        coordinates: Coordinate,
        move_anchors=False,
        **kwargs,
    ):
        super().move_to(coordinates=coordinates, **kwargs)

        if move_anchors:
            for part in self._anchored:
                part_coord = part.get_init_coordinates()
                part.move_to(
                    coordinates=part_coord, move_anchors=move_anchors, **kwargs
                )

    @property
    def _collision_type(self):
        return CollisionTypes.PART

    def update_team_filter(self):
        super().update_team_filter()

        for device in self._devices.values():
            device.update_team_filter()

    @property
    def action_space(self) -> spaces.Dict:

        sp = {'motor': self._action_space}

        for device in self.devices.values():
            if device.action_space:
                sp[device.name] = device.action_space

        return spaces.Dict(sp)

    @property
    @abstractmethod
    def _action_space(self):
        ...

    def apply_action(self, action: spaces.Dict):

        action_motor = action.get('motor', None)

        if action_motor:
            self._apply_action(action_motor)

        for device_name, device in self._devices.items():

            device_action = action.get(device_name, None)
            if device_action:
                device.apply_action(device_action)

    @abstractmethod
    def _apply_action(self, action):
        ...

    def pre_step(self):
        super().pre_step()
        for device in self._devices.values():
            device.pre_step()

    def post_step(self):
        super().post_step()
        for device in self._devices.values():
            device.post_step()

    def reset(self):
        super().reset()

        self._pm_body.velocity = (0, 0)
        self._pm_body.angular_velocity = 0

        for part in self._anchored:
            part.reset()

        for device in self._devices:
            device.reset()


class AnchoredPart(PhysicalPart, ABC):
    def __init__(
        self,
        rotation_range: float,
        **kwargs,
    ):

        super().__init__(
            **kwargs,
        )

        self._rotation_range = rotation_range

        self._anchor = None
        self._motor = None
        self._joint = None
        self._limit = None

        # Point on the anchor
        self._anchor_coordinates = ((0, 0), 0)

    @property
    def anchor(self):
        return self._anchor

    @anchor.setter
    def anchor(self, anchor):
        self._anchor = anchor

    # @property
    # def agent(self):
    # assert self._anchor
    # return self._anchor.agent

    @property
    def anchor_coordinates(self):
        return self._anchor_coordinates

    @anchor_coordinates.setter
    def anchor_coordinates(self, coord: Coordinate):
        self._anchor_coordinates = coord

    @property
    def relative_position(self):
        assert self._anchor
        return (self.position - self._anchor.position).rotated(-self._anchor.angle)

    @property
    def relative_angle(self):
        assert self._anchor
        rel_angle = (self.angle - self._anchor.angle) % (2 * math.pi)

        if rel_angle > math.pi:
            return rel_angle - 2 * math.pi
        return rel_angle

    def get_init_coordinates(self):
        """
        Calculates the position of a Part relative to its Anchor.
        Sets the position of the Part.
        """

        assert self._anchor

        pos_anchor = pymunk.Vec2d(*self._anchor_coordinates[0])
        pos_pivot = pymunk.Vec2d(*self._pivot_position)

        angle_offset_anchor = self._anchor_coordinates[1]

        position = (
            self._anchor.position
            + pos_anchor.rotated(self._anchor.angle)
            - pos_pivot.rotated(self._anchor.angle + angle_offset_anchor)
        )

        angle = self._anchor.pm_body.angle + angle_offset_anchor

        return position, angle

    def attach_to_anchor(self):

        assert self._anchor

        angle_offset_anchor = self._anchor_coordinates[1]

        # Create joint to attach to anchor
        self._joint = pymunk.PivotJoint(
            self._anchor.pm_body,
            self.pm_body,
            self._anchor_coordinates[0],
            self._pivot_position,
        )
        self._joint.collide_bodies = False
        self._limit = pymunk.RotaryLimitJoint(
            self._anchor.pm_body,
            self._pm_body,
            angle_offset_anchor - self._rotation_range / 2,
            angle_offset_anchor + self._rotation_range / 2,
        )

        self._motor = pymunk.SimpleMotor(self._anchor.pm_body, self.pm_body, 0)

    @property
    def pm_joints(self):
        assert self._joint and self._limit and self._motor
        return self._joint, self._limit, self._motor

    @property
    @abstractmethod
    def _pivot_position(self) -> pymunk.Vec2d:
        ...
