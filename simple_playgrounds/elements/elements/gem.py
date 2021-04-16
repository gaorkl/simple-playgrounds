"""
Module for Gem SceneElements.
Gem interacts with other SceneElements.
"""
from abc import ABC

from simple_playgrounds.scene_elements.element import SceneElement
from simple_playgrounds.utils.definitions import CollisionTypes, ElementTypes
from simple_playgrounds.utils.parser import parse_configuration


class GemElement(SceneElement, ABC):
    """
    A Gem interacts with other SceneElements.
    """

    def __init__(self, **kwargs):

        SceneElement.__init__(self,
                              visible_shape=True,
                              invisible_shape=False,
                              **kwargs)

    def _set_visible_shape_collision(self):
        self.pm_visible_shape.collision_type = CollisionTypes.GEM

    def _set_invisible_shape_collision(self):
        pass



class Coin(GemSceneElement):

    """Coins are used with a VendingMachine to get rewards.
    A Coin disappears when in contact with its VendingMachine."""

    entity_type = ElementTypes.COIN

    def __init__(self, vending_machine, **kwargs):

        super().__init__(**kwargs)
        self.vending_machine = vending_machine


class Key(GemSceneElement):

    """Keys are used to open Chests or Doors.
    A Key disappears when in contact with its VendingMachine."""

    entity_type = ElementTypes.KEY
