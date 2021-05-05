"""
Teleport can be used to teleport an agent.
"""
from typing import Union, List, Optional, Tuple
from abc import ABC

from simple_playgrounds.elements.element import TeleportElement, SceneElement
from simple_playgrounds.definitions import CollisionTypes, ElementTypes
from simple_playgrounds.common.position_utils import CoordinateSampler, Coordinate
from simple_playgrounds.agents import Agent


class TeleportToCoordinates(TeleportElement, ABC):

    def __init__(self,
                 destination: Union[CoordinateSampler, Coordinate],
                 **kwargs):

        super().__init__(destination, config_key=ElementTypes.BEAM, **kwargs)

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
                         config_key=ElementTypes.BEAM,
                         **kwargs)

    def _set_shape_collision(self):
        self.pm_invisible_shape.collision_type = CollisionTypes.TELEPORT


class VisibleBeam(TeleportToCoordinates):

    def __init__(self,
                 destination: Union[CoordinateSampler, Coordinate],
                 **kwargs):

        super().__init__(destination,
                         visible_shape=True,
                         invisible_shape=False,
                         config_key=ElementTypes.BEAM,
                         **kwargs)

    def _set_shape_collision(self):
        self.pm_visible_shape.collision_type = CollisionTypes.TELEPORT


class TeleportToElement(TeleportElement, ABC):

    def __init__(self,
                 destination: SceneElement,
                 config_key,
                 relative: bool = False,
                 **kwargs):

        super().__init__(destination, visible_shape=True, invisible_shape=False, config_key=config_key, **kwargs)

        self._relative = relative

    def energize(self, agent: Agent):

         if self._relative:

             # teleport relative to destination angle

         else:

             # teleport is absolute, keep world orientation.

        return self.beam_coordinates

    def _set_shape_collision(self):
        self.pm_visible_shape.collision_type = CollisionTypes.TELEPORT




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


class TeleportElement(SceneElement, ABC):
    def __init__(self, texture=(0, 100, 100), **kwargs):
        super().__init__(texture=texture, **kwargs)
        self.pm_invisible_shape.collision_type = CollisionTypes.TELEPORT

        self.reward = 0
        self.reward_provided = False

        self.target = None

    def add_target(self, target):
        self.target = target
