"""
Teleport can be used to teleport an agent.
"""
from simple_playgrounds.scene_elements.element import SceneElement
from simple_playgrounds.definitions import CollisionTypes


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
