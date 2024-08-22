from __future__ import annotations

from abc import abstractmethod


class ObservationMixin:
    @property
    @abstractmethod
    def observation_space(self):
        ...

    @property
    @abstractmethod
    def observation(self):
        ...


class SensorMixin:
    @property
    @abstractmethod
    def observation_space(self):
        ...

    @property
    @abstractmethod
    def observation(self):
        ...
