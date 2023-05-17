from abc import ABC

from .sensor import ExternalSensor


class AreaSensor(ExternalSensor, ABC):
    """
    Base class for Area sensor.
    Area sensors use Pymunk shape detection to detect shapes within a certain radius.
    """
