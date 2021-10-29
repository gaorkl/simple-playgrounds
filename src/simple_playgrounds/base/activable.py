from abc import ABC, abstractmethod
from typing import Optional, Any


class Activable(ABC):

    def __init__(self):
        self._activated_by: Optional[Any] = None

    def pre_step(self):
        self._activated_by = None

    def activate(self, activator):

        self._activate(activator)
        self._activated_by = activator

    @abstractmethod
    def _activate(self, activator):
        ...

    @property
    def activated_by(self):
        return self._activated_by

    @property
    def activated(self):
        return bool(self._activated_by)
