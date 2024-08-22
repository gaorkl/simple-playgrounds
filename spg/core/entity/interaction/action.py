from __future__ import annotations

from abc import abstractmethod


class ActionMixin:
    @property
    @abstractmethod
    def _action_space(self):
        ...

    @property
    def action_space(self):
        return self._action_space

    @abstractmethod
    def _apply_action(self, action):
        ...

    def apply_action(self, action):
        self._apply_action(action)
