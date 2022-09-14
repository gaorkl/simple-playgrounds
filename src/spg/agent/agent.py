# pylint: disable=too-many-public-methods

""" Contains the base class for agents.

Agent class should be inherited to create agents.
It is possible to define custom Agent with
body parts, sensors and corresponding Keyboard controllers.

Examples can be found in spg/agents/agents.py

"""
from __future__ import annotations

from typing import Dict, List, Optional, Union

import numpy as np

from ..element import Teleporter
from ..entity import EmbodiedEntity, Entity
from ..utils.position import Coordinate
from .communicator import Communicator
from .controller import Command, Controller
from .part import PhysicalPart
from .sensor import Sensor

_BORDER_IMAGE = 3

Commands = Dict[Controller, Command]


class Agent(Entity):

    """
    Base class for building agents.
    Agents are composed of a base and parts which are attached to the base
    or to each other.
    Each part has actuators allowing for control of the agent.
    The base has no actuator.

    Attributes:
        name: name of the agent.
            Either provided by the user or generated using internal counter.
        base: Main part of the agent. Can be mobile or fixed.
        parts: Different parts attached to the base or to other parts.
        actuators:
        sensors:
        initial_coordinates:
    """

    _index_agent: int = 0

    def __init__(
        self,
        **kwargs,
    ):

        super().__init__(**kwargs)

        self._name_count = {}
        self._name_to_controller = {}

        # Body parts
        self._parts: List[PhysicalPart] = []

        # Reward
        self._reward: float = 0

        # Teleport
        self._teleported_to: Optional[Union[Coordinate, Teleporter]] = None

        self._initial_coordinates = None
        self._allow_overlapping = False

    def add(self, part: PhysicalPart):
        part.agent = self
        part.teams = self._teams

        for device in part.devices:
            device.teams = self._teams

        self._parts.append(part)

    ################
    # Properties
    ################

    @property
    def base(self):
        return self._parts[0]

    @property
    def initial_coordinates(self):
        return self._initial_coordinates

    @initial_coordinates.setter
    def initial_coordinates(self, init_coord):
        self._initial_coordinates = init_coord
        self._parts[0].initial_coordinates = init_coord

    @property
    def allow_overlapping(self):
        return self._allow_overlapping

    @allow_overlapping.setter
    def allow_overlapping(self, allow):
        self._allow_overlapping = allow
        self._parts[0].allow_overlapping = allow

    @property
    def position(self):
        return self.base.position

    @property
    def angle(self):
        return self.base.angle

    ################
    # Observations
    ################

    @property
    def observations(self):
        return {
            sens: sens.sensor_values
            for part in self._parts
            for sens in part.devices
            if isinstance(sens, Sensor)
        }

    @property
    def controllers(self):
        return [
            contr
            for part in self._parts
            for contr in part.devices
            if isinstance(contr, Controller)
        ]

    @property
    def communicators(self):
        return [
            comm
            for part in self._parts
            for comm in part.devices
            if isinstance(comm, Communicator)
        ]

    @property
    def sensors(self):
        return [
            sensor
            for part in self._parts
            for sensor in part.devices
            if isinstance(sensor, Sensor)
        ]

    def compute_observations(self):
        pass

    def compute_rewards(self):
        pass

    ################
    # Commands
    ################

    @property
    def parts(self):
        return self._parts

    @property
    def default_commands(self) -> Commands:
        return {controller: controller.default for controller in self.controllers}

    def receive_commands(self, commands: Commands):

        # Set command values
        if isinstance(commands, np.ndarray):
            for index, controller in enumerate(self.controllers):
                controller.command = commands[index]
            return

        for controller, command in commands.items():
            if isinstance(controller, str):
                controller = self._name_to_controller[controller]

            controller.command = command

    def apply_commands(self):
        # Apply command to playground physics
        for part in self._parts:
            part.apply_commands()

    ################
    # Rewards
    ################

    @property
    def reward(self):
        return self._reward

    @reward.setter
    def reward(self, rew):
        self._reward = rew

    #############
    # ADD PARTS AND SENSORS
    #############

    def update_team_filter(self):
        for part in self._parts:
            part.update_team_filter()

    ##############
    # CONTROL
    ##############

    def pre_step(self, **kwargs):
        """
        Reset actuators and reward to 0 before a new step of the environment.
        """

        self._reward = 0
        self._update_teleport(**kwargs)

        for part in self._parts:
            part.pre_step(**kwargs)

    def reset(self):
        for part in self._parts:
            part.reset()

    def post_step(self, **kwargs):
        for part in self._parts:
            part.post_step(**kwargs)

    ###############
    # PLAYGROUND INTERACTIONS
    ###############

    def move_to(self, coord: Coordinate, **kwargs):
        """
        After moving, the agent body is back in its original configuration.
        Default angle, etc.
        """
        self.base.move_to(coordinates=coord, move_anchors=True, **kwargs)

    @property
    def teleported_to(self):
        return self._teleported_to

    @teleported_to.setter
    def teleported_to(self, destination):
        self._teleported_to = destination

    def _update_teleport(self):

        if isinstance(self._teleported_to, Teleporter):
            if self._overlaps(self._teleported_to):
                return

        self._teleported_to = None

    def _overlaps(
        self,
        entity: EmbodiedEntity,
    ) -> bool:

        assert self._playground

        for part in self.parts:
            if self._playground.overlaps(part, entity):
                return True

        return False
