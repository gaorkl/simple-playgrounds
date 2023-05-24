from __future__ import annotations

from abc import abstractmethod


class ActionMixin:
    @property
    @abstractmethod
    def action_space(self):
        ...

    @abstractmethod
    def apply_action(self, action):
        ...
