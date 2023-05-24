from abc import ABC

from spg.core.entity.sensor import SensorMixin


class InternalSensor(SensorMixin, ABC):
    pass

