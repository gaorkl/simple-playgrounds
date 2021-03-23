"""
Teleport can be used to teleport an agent.
"""
from simple_playgrounds.playgrounds.scene_elements.element import SceneElement
from simple_playgrounds.utils.definitions import CollisionTypes, SceneElementTypes

# pylint: disable=line-too-long


class Teleport(SceneElement):

    entity_type = SceneElementTypes.TELEPORT
    interactive = True
    traversable = True

    def __init__(self, texture=(0, 100, 100), **kwargs):
        super().__init__(texture=texture, **kwargs)
        self.pm_interaction_shape.collision_type = CollisionTypes.TELEPORT

        self.reward = 0
        self.reward_provided = False

        self.target = None

    def add_target(self, target):
        self.target = target
