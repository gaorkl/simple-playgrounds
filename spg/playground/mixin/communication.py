from typing import Dict, List

from spg.entity.mixin.communication import CommunicationMixin


class CommunicationManager:
    def __init__(self, **kwargs) -> None:
        self._topics: Dict[str, List[CommunicationMixin]] = {}
        self._communicators: List[CommunicationMixin] = []

    def subscribe(self, communicator: CommunicationMixin, topic: str):
        """Subscribe to a topic."""
        if topic not in self._topics:
            self._topics[topic] = []
        self._topics[topic].append(communicator)
        self._communicators.append(communicator)

    def unsubscribe(self, communicator, topic):
        """Unsubscribe from a topic."""
        if topic in self._topics:
            self._topics[topic].remove(communicator)

    def publish(self, sender, topic, message):
        """Publish a message to all subscribed topics."""

        for receiver in self._topics[topic]:
            if receiver is not sender and self.in_communication_range(sender, receiver):
                receiver.receive_message(message)

    def clear_messages(self):
        """Clear all topics."""
        for comm in self._communicators:
            comm.received_messages = []

    def in_communication_range(
        self, sender: CommunicationMixin, receiver: CommunicationMixin
    ):

        distance = sender.position.get_distance(receiver.position)

        if sender.communication_range is None or receiver.communication_range is None:
            return True

        return (
            distance <= sender.communication_range
            and distance <= receiver.communication_range
        )
