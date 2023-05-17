from __future__ import annotations

from abc import abstractmethod
from typing import TYPE_CHECKING, List

from gymnasium import spaces

from spg.entity.mixin import ActionMixin, ObservationMixin

if TYPE_CHECKING:
    from spg.playground import Playground


class CommunicationMixin(ActionMixin, ObservationMixin):

    playground: Playground
    name: str

    received_messages: List

    def subscribe_to_topics(self):

        for topic in self.topics:
            self.playground.subscribe(self, topic)

        self.received_messages = []

    def unsubscribe_from_topics(self):
        for topic in self.topics:
            self.playground.unsubscribe(self, topic)

    @property
    @abstractmethod
    def communication_range(self):
        ...

    @property
    @abstractmethod
    def topics(self) -> List[str]:
        ...

    @property
    @abstractmethod
    def message_space(self) -> spaces.Space:
        ...

    @property
    def action_space(self):
        return spaces.Dict({topic: self.message_space for topic in self.topics})

    @property
    def observation_space(self):
        return spaces.Sequence(self.message_space)

    def receive_message(self, message):
        self.received_messages.append(message)

    @property
    def observation(self):
        return self.received_messages

    def apply_action(self, action):
        for topic, message in action.items():
            self.playground.publish(self, topic, message)
