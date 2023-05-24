import arcade
from gymnasium import spaces

from spg.core.entity import Entity
from spg.core.entity.communication import CommunicationMixin
from spg.core.entity.mixin import AttachedStaticMixin
from spg.core.entity.mixin.sprite import get_texture_from_geometry
from tests.mock_agents import StaticAgent


class SimpleCommunicator(Entity, AttachedStaticMixin, CommunicationMixin):
    def __init__(self, message_length, communication_range, topics=None):

        self._message_length = message_length
        self._communication_range = communication_range

        if topics is None:
            topics = []
        elif isinstance(topics, str):
            topics = [topics]
        else:
            topics = list(topics)

        self._topics = topics

        texture = get_texture_from_geometry(
            "circle", color=arcade.color.CYAN, radius=3
        )[0]

        super().__init__(ghost=True, texture=texture)

    @property
    def topics(self):
        return self._topics

    @property
    def communication_range(self):
        return self._communication_range

    @property
    def message_space(self) -> spaces.Space:
        return spaces.Text(self._message_length)

    @property
    def attachment_point(self):
        return 0, 0


class MockAgentWithCommunication(StaticAgent):
    def __init__(self, message_length, communication_range=None, topics=None, **kwargs):

        super().__init__(**kwargs)

        self.communicator = SimpleCommunicator(
            message_length=message_length,
            communication_range=communication_range,
            topics=topics,
        )
        self.add(self.communicator)
