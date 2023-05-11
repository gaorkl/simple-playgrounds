from typing import List

from gymnasium import spaces

from spg.entity.mixin import ActionMixin, ObservationMixin


class CommunicationMixin(ActionMixin, ObservationMixin):

    _message_space: spaces.Space
    _received_messages: List = []
    _recipients: Optional[List] = None

    @property
    def observation_space(self):
        return spaces.Sequence(self._message_space)

    def get_observation(self):
        return self._received_messages

    def receive_messages(self):
        pass

    def apply_action(self, action):
        self.send_messages(action)

    def send_messages(self):

    def publish(self, topic, message, recipient=None):
        """Publish a message to a topic."""
        if topic in self._topics:
            for func in self._topics[topic]:
                if recipient is None:  # Broadcast to all agents
                    if self.in_range(func.__self__):
                        func(message)
                elif isinstance(recipient, str):  # Address to a specific agent
                    if recipient == func.__self__.name and self.in_range(func.__self__):
                        func(message)
                elif isinstance(recipient, list):  # Address to a team of agents
                    if func.__self__.name in recipient and self.in_range(func.__self__):
                        func(message)
