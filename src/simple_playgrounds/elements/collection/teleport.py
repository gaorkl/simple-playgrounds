"""
Teleport can be used to teleport an agent.
"""
from typing import Union, Optional
from abc import ABC
from math import pi
from enum import Enum

from pymunk import Vec2d

from ..element import TeleportElement, SceneElement
from simple_playgrounds.common.definitions import CollisionTypes, ElementTypes
from .basic import Traversable
from ...common.position_utils import CoordinateSampler, Coordinate
from ...agents.agent import Agent

class PortalColor(Enum):

    RED = (255, 0, 0)
    GREEN = (0, 255, 0)
    BLUE = (0, 0, 255)


class TeleportToCoordinates(TeleportElement, ABC):

    def __init__(self,
                 destination: Union[CoordinateSampler, Coordinate],
                 **kwargs):

        super().__init__(destination=destination, config_key=ElementTypes.BEAM, **kwargs)

        if not isinstance(destination, CoordinateSampler):
            assert len(destination) == 2 and len(destination[0]) == 2

    def energize(self, agent: Agent):

        if isinstance(self.destination, CoordinateSampler):
            return self.destination.sample()

        return self.destination


class InvisibleBeam(TeleportToCoordinates):

    def __init__(self,
                 destination: Union[CoordinateSampler, Coordinate],
                 **kwargs):

        super().__init__(destination,
                         visible_shape=False,
                         invisible_shape=True,
                         **kwargs)

    def _set_shape_collision(self):
        self.pm_invisible_shape.collision_type = CollisionTypes.TELEPORT


class VisibleBeam(TeleportToCoordinates):

    def __init__(self,
                 destination: Union[CoordinateSampler, Coordinate],
                 **kwargs):

        super().__init__(destination,
                         visible_shape=True,
                         invisible_shape=True,
                         **kwargs)

    def _set_shape_collision(self):
        self.pm_invisible_shape.collision_type = CollisionTypes.TELEPORT


class TeleportToElement(TeleportElement, ABC):

    def __init__(self,
                 destination: Optional[SceneElement],
                 config_key: ElementTypes,
                 relative_teleport: bool = True,
                 **kwargs):

        super().__init__(destination=destination, config_key=config_key, **kwargs)

        self.relative_teleport = relative_teleport

    def energize(self, agent: Agent):

        relative_position = Vec2d(*agent.position) - self.position

        if not self.destination:
            raise ValueError("Destination should be set")

        assert isinstance(self.destination, SceneElement)

        # How far from center?
        if not isinstance(self.destination, Traversable):
            distance = self.destination.radius + agent.base_platform.radius + 2
        else:
            distance = 0

        if self.relative_teleport:
            new_pos = self.destination.position \
                      + relative_position.rotated(self.destination.angle).normalized()*distance
            new_orientation = agent.angle - self.angle + self.destination.angle + pi

        else:
            new_pos = Vec2d(*self.destination.position) + relative_position.rotated(pi).normalized()*distance
            new_orientation = agent.angle

        return tuple(new_pos), new_orientation


class VisibleBeamHoming(TeleportToElement):

    def __init__(self,
                 destination: Optional[SceneElement],
                 **kwargs,
                 ):

        super().__init__(destination=destination,
                         visible_shape=True,
                         invisible_shape=True,
                         config_key=ElementTypes.BEAM_HOMING,
                         **kwargs,
                         )

    def _set_shape_collision(self):
        self.pm_invisible_shape.collision_type = CollisionTypes.TELEPORT


class InvisibleBeamHoming(TeleportToElement):

    def __init__(self,
                 destination: Optional[SceneElement],
                 **kwargs,
                 ):

        super().__init__(destination=destination,
                         visible_shape=False,
                         invisible_shape=True,
                         config_key=ElementTypes.BEAM_HOMING,
                         **kwargs,
                         )

    def _set_shape_collision(self):
        self.pm_invisible_shape.collision_type = CollisionTypes.TELEPORT


class Portal(TeleportElement):

    def __init__(self,
                 color: PortalColor):

        super().__init__(destination=None,
                         visible_shape=True,
                         invisible_shape=True,
                         config_key=ElementTypes.PORTAL,
                         texture=color.value)

    def _set_shape_collision(self):
        self.pm_invisible_shape.collision_type = CollisionTypes.TELEPORT

    def energize(self, agent: Agent):

        relative_position = Vec2d(*agent.position) - self.position

        if not self.destination:
            raise ValueError("Destination should be set")

        assert isinstance(self.destination, Portal)

        new_pos = self.destination.position \
                  + relative_position.rotated(self.destination.angle - self.angle)
        new_orientation = agent.angle - self.angle + self.destination.angle + pi

        return tuple(new_pos), new_orientation


# pylint: disable=line-too-long

# TELEPORT ELEMENTS

#
# if teleport.target.traversable:
#     agent.position = teleport.target.position
#
# else:
#     area_shape = teleport.target.physical_shape
#     if area_shape == 'rectangle':
#         width = teleport.target.width + agent.base_platform.radius * 2 + 1
#         length = teleport.target.length + agent.base_platform.radius * 2 + 1
#         angle = teleport.target.angle
#         sampler = CoordinateSampler(
#             center=teleport.target.position,
#             area_shape=area_shape,
#             angle=angle,
#             width_length=[width + 2, length + 2],
#             excl_width_length=[width, length],
#         )
#     else:
#         radius = teleport.target.radius + agent.base_platform.radius + 1
#         sampler = CoordinateSampler(
#             center=teleport.target.position,
#             area_shape='circle',
#             radius=radius,
#             excl_radius=radius,
#         )
#
#     agent.coordinates = sampler.sample()
#
#
#
# class TeleportElement(SceneElement, ABC):
#     def __init__(self, texture=(0, 100, 100), **kwargs):
#         super().__init__(texture=texture, **kwargs)
#         self.pm_invisible_shape.collision_type = CollisionTypes.TELEPORT
#
#         self.reward = 0
#         self.reward_provided = False
#
#         self.target = None
#
#     def add_target(self, target):
#         self.target = target
