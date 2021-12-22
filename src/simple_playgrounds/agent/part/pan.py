from __future__ import annotations

import math
from abc import ABC
from enum import IntEnum, auto
from typing import Tuple, TYPE_CHECKING, Optional, List
if TYPE_CHECKING:
    from simple_playgrounds.agent.agent import Agent
    from simple_playgrounds.agent.actuator.actuators import ActuatorDevice

import pymunk

from simple_playgrounds.common.definitions import ARM_MAX_FORCE, CollisionTypes
from simple_playgrounds.entity.entity import Entity
from simple_playgrounds.configs.parser import parse_configuration


