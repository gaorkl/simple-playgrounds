from abc import ABC

from .sensor import ExternalSensor


class TopDownSensor(ExternalSensor, ABC):

    """
    Base class for Image Based sensors.
    Image based sensors are computed using the top-down rendering of the playground.

    """
