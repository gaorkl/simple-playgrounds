"""
Teleport can be used to teleport an agent.
"""
from .basic import Traversable
from ....utils.definitions import CollisionTypes

#pylint: disable=line-too-long


class Teleport(Traversable):

    entity_type = 'teleport'
    interactive = True

    def __init__(self, initial_position, texture=(0, 100, 100), **kwargs):
        super().__init__(initial_position=initial_position, texture=texture, **kwargs)
        self.pm_interaction_shape.collision_type = CollisionTypes.TELEPORT

        self.reward = 0
        self.reward_provided = False

        self.target = None

    def add_target(self, target):
        self.target = target
