"""
Module for Gem SceneElements.
Gem interacts with other SceneElements.
"""
from abc import ABC

from simple_playgrounds.scene_elements.element import SceneElement
from simple_playgrounds.utils.definitions import CollisionTypes, ElementTypes
from simple_playgrounds.utils.parser import parse_configuration





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
