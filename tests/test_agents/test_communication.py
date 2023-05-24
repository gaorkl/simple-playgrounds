import pytest

from spg.core.playground import EmptyPlayground
from tests.mock_communicator import MockAgentWithCommunication


@pytest.mark.parametrize("message_length", [1, 10, 30])
@pytest.mark.parametrize("communication_range", [None, 10, 100, 200])
def test_equip_communication(communication_range, message_length):
    playground = EmptyPlayground(size=(1000, 1000))

    agent_1 = MockAgentWithCommunication(
        name="agent_1",
        message_length=message_length,
        communication_range=communication_range,
    )
    playground.add(agent_1, ((100, 100), 0))


@pytest.mark.parametrize(
    "range_sender, range_receiver, distance, in_range",
    [
        (100, 100, 50, True),
        (200, 50, 100, False),
        (50, 200, 100, False),
        (100, None, 80, True),
        (None, None, 100, True),
        (None, 100, 200, True),
    ],
)
def test_transmission_range(range_sender, range_receiver, distance, in_range):
    playground = EmptyPlayground(size=(1000, 1000))

    agent_1 = MockAgentWithCommunication(
        name="agent_1",
        communication_range=range_sender,
        message_length=1,
        topics="test",
    )
    agent_2 = MockAgentWithCommunication(
        name="agent_2",
        communication_range=range_receiver,
        message_length=1,
        topics=["test"],
    )

    playground.add(agent_1, ((100, 100), 0))
    playground.add(agent_2, ((100 + distance, 100), 0))

    assert (
        playground.in_communication_range(agent_1.communicator, agent_2.communicator)
        == in_range
    )

    action = playground.action_space.sample()

    obs, *_ = playground.step(action)

    # convert nested ordered dict to dict

    if in_range:
        sent_1 = action[agent_1.name][agent_1.communicator.name]["test"]
        sent_2 = action[agent_2.name][agent_2.communicator.name]["test"]

        rec_1 = agent_1.communicator.received_messages[0]
        rec_2 = agent_2.communicator.received_messages[0]

        assert sent_1 == rec_2
        assert sent_2 == rec_1


def test_directed_broadcast():

    # by default, agents create a topic with their own name

    playground = EmptyPlayground(size=(1000, 1000))

    agent_1 = MockAgentWithCommunication(
        name="agent_1", message_length=1, topics=["agent_1_2"]
    )
    agent_2 = MockAgentWithCommunication(
        name="agent_2", message_length=1, topics=["agent_1_2", "private"]
    )
    agent_3 = MockAgentWithCommunication(
        name="agent_3", message_length=1, topics=["private"]
    )
    agent_4 = MockAgentWithCommunication(
        name="agent_4", message_length=1, topics=["private"]
    )
    agent_5 = MockAgentWithCommunication(name="agent_5", message_length=1)

    playground.add(agent_1, ((100, 100), 0))
    playground.add(agent_2, ((200, 100), 0))
    playground.add(agent_3, ((100, 200), 0))
    playground.add(agent_4, ((200, 200), 0))
    playground.add(agent_5, ((300, 100), 0))

    playground.step(playground.action_space.sample())

    assert len(agent_1.communicator.received_messages) == 1
    assert len(agent_2.communicator.received_messages) == 3
    assert len(agent_3.communicator.received_messages) == 2
    assert len(agent_4.communicator.received_messages) == 2
    assert len(agent_5.communicator.received_messages) == 0
