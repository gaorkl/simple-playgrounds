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
 
class Head(AnchoredPart):
    """
    Circular Part, attached on its center.
    Not colliding with any Entity or Part.

    """
    def __init__(self,
                 anchor,
                 position_anchor=(0, 0),
                 angle_offset=0,
                 **kwargs):
        default_config = parse_configuration('agent_parts', PartTypes.HEAD)
        kwargs = {**default_config, **kwargs}

        super().__init__(anchor,
                         position_anchor=position_anchor,
                         angle_offset=angle_offset,
                         **kwargs)

        self.pm_visible_shape.sensor = True


class Eye(AnchoredPart):
    """
    Circular Part, attached on its center.
    Not colliding with any Entity or Part

    """
    def __init__(self,
                 anchor,
                 position_anchor=(0, 0),
                 angle_offset=0,
                 **kwargs):
        default_config = parse_configuration('agent_parts', PartTypes.EYE)
        kwargs = {**default_config, **kwargs}

        super().__init__(anchor,
                         position_anchor=position_anchor,
                         angle_offset=angle_offset,
                         **kwargs)

        self.pm_visible_shape.sensor = True


class Hand(AnchoredPart):
    """
    Circular Part, attached on its center.
    Is colliding with other Entity or Part, except from anchor and other Parts attached to it.

    """
    def __init__(self,
                 anchor,
                 position_anchor=(0, 0),
                 angle_offset=0,
                 **kwargs):
        default_config = parse_configuration('agent_parts', PartTypes.HAND)
        kwargs = {**default_config, **kwargs}

        super().__init__(anchor,
                         position_anchor=position_anchor,
                         angle_offset=angle_offset,
                         **kwargs)

        self.pm_visible_shape.sensor = True



