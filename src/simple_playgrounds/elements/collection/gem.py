"""
Module for Gem SceneElements.
Gem interacts with other SceneElements.
"""
from typing import Union

from ..element import GemElement
from simple_playgrounds.common.definitions import ElementTypes
from .activable import Lock, Chest


class Coin(GemElement):
    """Coins are used with a VendingMachine to get rewards.
    A Coin disappears when in contact with its VendingMachine."""
    def __init__(self, vending_machine, **kwargs):

        super().__init__(config_key=ElementTypes.COIN,
                         elem_activated=vending_machine,
                         **kwargs,
                         )


class Key(GemElement):
    """Keys are used to open Chests or Doors.
    A Key disappears when in contact with its VendingMachine."""
    def __init__(self, locked_elem: Union[Lock, Chest], **kwargs):

        super().__init__(config_key=ElementTypes.KEY,
                         elem_activated=locked_elem,
                         **kwargs,
                         )
