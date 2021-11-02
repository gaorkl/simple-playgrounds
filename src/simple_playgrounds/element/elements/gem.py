"""
Module for Gem SceneElements.
Gem interacts with other SceneElements.
"""
from abc import ABC
from typing import Union, Optional

from .activable import Lock, Chest, ActivableByGem
from ..element import SceneElement
from ...common.definitions import ElementTypes, CollisionTypes
from ...configs.parser import parse_configuration


class GemElement(SceneElement, ABC):
    """
    A Gem interacts with other SceneElements.
    """
    def __init__(self,
                 elem_activated: ActivableByGem,
                 config_key: Optional[Union[ElementTypes, str]] = None,
                 **entity_params):

        default_config = parse_configuration('element_gem', config_key)
        entity_params = {**default_config, **entity_params}

        SceneElement.__init__(self,
                              visible_shape=True,
                              invisible_shape=False,
                              **entity_params)

        self.elem_activated = elem_activated

    def _set_shape_collision(self):
        self.pm_visible_shape.collision_type = CollisionTypes.GEM


class Coin(GemElement):
    """Coins are used with a VendingMachine to get rewards.
    A Coin disappears when in contact with its VendingMachine."""
    def __init__(self, vending_machine, **kwargs):

        super().__init__(
            config_key=ElementTypes.COIN,
            elem_activated=vending_machine,
            **kwargs,
        )


class Key(GemElement):
    """Keys are used to open Chests or Doors.
    A Key disappears when in contact with its VendingMachine."""
    def __init__(self, locked_elem: Union[Lock, Chest], **kwargs):

        super().__init__(
            config_key=ElementTypes.KEY,
            elem_activated=locked_elem,
            **kwargs,
        )
