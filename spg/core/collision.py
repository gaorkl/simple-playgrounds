from __future__ import annotations

from enum import IntEnum, auto


class CollisionTypes(IntEnum):
    NONE = auto()
    TRIGGER = auto()
    AGENT = auto()
    ACTIVABLE = auto()
