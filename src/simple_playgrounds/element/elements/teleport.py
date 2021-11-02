"""
Teleport can be used to teleport an agent.
"""
from __future__ import annotations
from abc import ABC, abstractmethod
from enum import Enum
from math import pi
from typing import Union, Optional, Tuple, TYPE_CHECKING
if TYPE_CHECKING:
    from simple_playgrounds.agent.agent import Agent

from pymunk import Vec2d

from simple_playgrounds.element.elements.basic import Traversable
from simple_playgrounds.element.element import SceneElement
from simple_playgrounds.common.definitions import CollisionTypes, ElementTypes
from simple_playgrounds.common.position_utils import CoordinateSampler, Coordinate
from simple_playgrounds.configs.parser import parse_configuration


class PortalColor(Enum):

    RED = (255, 0, 0)
    GREEN = (0, 255, 0)
    BLUE = (0, 0, 255)


class TeleportElement(SceneElement, ABC):
    """ Base Class for Teleport Entities"""
    def __init__(
        self,
        destination: Optional[Union[Coordinate, CoordinateSampler,
                                    SceneElement]],
        config_key: Optional[Union[ElementTypes, str]] = None,
        keep_inertia: bool = True,
        **entity_params,
    ):

        default_config = parse_configuration('element_teleport', config_key)
        entity_params = {**default_config, **entity_params}

        super().__init__(**entity_params)

        self._destination = destination
        self.keep_inertia = keep_inertia

    def energize(self, agent: Agent):

        new_position, new_angle = self._calculate_new_coordinates(agent)
        delta_angle = agent.angle - new_angle
        agent.position, agent.angle = new_position, new_angle

        if self.keep_inertia:
            agent.velocity = Vec2d(
                *agent.velocity).rotated(-delta_angle)
        else:
            agent.velocity = (0, 0)

        if isinstance(self._destination, TeleportElement):
            agent.has_teleported_to(self._destination)
        else:
            agent.has_teleported_to( (new_position, new_angle) )

    @abstractmethod
    def _calculate_new_coordinates(self, agent: Agent):
        pass

    @property
    def destination(self):

        if not self._destination:
            raise ValueError("Destination not set")

        return self._destination

    @destination.setter
    def destination(self, destination):

        self._destination = destination


class TeleportToCoordinates(TeleportElement, ABC):
    def __init__(self, destination: Union[CoordinateSampler, Coordinate],
                 **kwargs):

        super().__init__(destination=destination,
                         config_key=ElementTypes.BEAM,
                         **kwargs)

        if not isinstance(destination, CoordinateSampler):
            assert len(destination) == 2 and len(destination[0]) == 2

    def _calculate_new_coordinates(self, agent: Agent):

        if isinstance(self.destination, CoordinateSampler):
            return self.destination.sample()

        return self.destination


class InvisibleBeam(TeleportToCoordinates):
    def __init__(self, destination: Union[CoordinateSampler, Coordinate],
                 **kwargs):

        super().__init__(destination,
                         visible_shape=False,
                         invisible_shape=True,
                         **kwargs)

    def _set_shape_collision(self):
        self.pm_invisible_shape.collision_type = CollisionTypes.TELEPORT


class VisibleBeam(TeleportToCoordinates):
    def __init__(self, destination: Union[CoordinateSampler, Coordinate],
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

        super().__init__(destination=destination,
                         config_key=config_key,
                         **kwargs)

        self.relative_teleport = relative_teleport

    def _calculate_new_coordinates(self, agent: Agent):

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
            new_pos = Vec2d(
                *self.destination.position
            ) + relative_position.rotated(pi).normalized() * distance
            new_orientation = agent.angle

        return tuple(new_pos), new_orientation


class VisibleBeamHoming(TeleportToElement):
    def __init__(
        self,
        destination: Optional[SceneElement],
        **kwargs,
    ):

        super().__init__(
            destination=destination,
            visible_shape=True,
            invisible_shape=True,
            config_key=ElementTypes.BEAM_HOMING,
            **kwargs,
        )

    def _set_shape_collision(self):
        self.pm_invisible_shape.collision_type = CollisionTypes.TELEPORT


class InvisibleBeamHoming(TeleportToElement):
    def __init__(
        self,
        destination: Optional[SceneElement],
        **kwargs,
    ):

        super().__init__(
            destination=destination,
            visible_shape=False,
            invisible_shape=True,
            config_key=ElementTypes.BEAM_HOMING,
            **kwargs,
        )

    def _set_shape_collision(self):
        self.pm_invisible_shape.collision_type = CollisionTypes.TELEPORT


class Portal(TeleportElement):
    def __init__(
        self,
        color: Union[PortalColor, Tuple[int, int, int]],
    ):

        if isinstance(color, PortalColor):
            color = color.value

        assert len(color) == 3

        super().__init__(destination=None,
                         visible_shape=True,
                         invisible_shape=True,
                         config_key=ElementTypes.PORTAL,
                         texture=color)

    def _set_shape_collision(self):
        self.pm_invisible_shape.collision_type = CollisionTypes.TELEPORT

    def _calculate_new_coordinates(self, agent: Agent):

        relative_position = Vec2d(*agent.position) - self.position

        if not self.destination:
            raise ValueError("Destination should be set")

        assert isinstance(self.destination, Portal)

        new_pos = self.destination.position \
                  + relative_position.rotated(self.destination.angle - self.angle)
        new_orientation = agent.angle - self.angle + self.destination.angle + pi

        return tuple(new_pos), new_orientation
