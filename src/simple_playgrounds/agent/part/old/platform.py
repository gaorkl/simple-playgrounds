from abc import ABC
from typing import TYPE_CHECKING

from simple_playgrounds.agent.part.part import Part


class Platform(Part, ABC):
    """
    Base class for Platforms.
    Platform can move in space using force actuators that propels them.
    """
    pass


class MobilePlatform(Platform):
    """
        Platform that is movable.

    """
    def __init__(self, **kwargs):
        super().__init__(movable=True, **kwargs)


# class FixedPlatform(Platform):
#     """
#         Platform that is fixed.
#         Can be used to build Arms with fixed base.
#         Refer to the base class Platform.

#     """
#     def __init__(self, can_absorb, **kwargs):
#         super().__init__(can_absorb=can_absorb, movable=False, **kwargs)



