"""
Module for Gem SceneElements.
Gem interacts with other SceneElements.
"""
from abc import ABC

from simple_playgrounds.playgrounds.scene_elements.element import SceneElement
from simple_playgrounds.utils.definitions import CollisionTypes, SceneElementTypes
from simple_playgrounds.utils.parser import parse_configuration


class GemSceneElement(SceneElement, ABC):
    """
    A Gem interacts with other SceneElements.
    """

    movable = True
    background = False

    def __init__(self, **kwargs):

        default_config = parse_configuration('element_interactive', self.entity_type)
        entity_params = {**default_config, **kwargs}

        SceneElement.__init__(self, **entity_params)
        self.pm_visible_shape.collision_type = CollisionTypes.GEM


class Coin(GemSceneElement):

    """Coins are used with a VendingMachine to get rewards.
    A Coin disappears when in contact with its VendingMachine."""

    entity_type = SceneElementTypes.COIN

    def __init__(self, vending_machine, **kwargs):

        super().__init__(**kwargs)
        self.vending_machine = vending_machine


class Key(GemSceneElement):

    """Keys are used to open Chests or Doors.
    A Key disappears when in contact with its VendingMachine."""

    entity_type = SceneElementTypes.KEY
