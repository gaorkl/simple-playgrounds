import pytest

from spg.agent.device.communicator import Communicator, LimitedCommunicator
from spg.playground import Playground
from tests.mock_agents import MockAgent


def test_equip_communication(comm_radius):

    playground = Playground()

    agent_1 = MockAgent(name="agent_1")
    comm_1 = Communicator(transmission_range=comm_radius)
    agent_1.base.add(comm_1)

    agent_2 = MockAgent(name="agent_2")
    comm_2 = Communicator(transmission_range=comm_radius)
    agent_2.base.add(comm_2)

    playground.add(agent_1, ((100, 100), 0))
    playground.add(agent_2, ((200, 100), 0))


@pytest.mark.parametrize(
    "range_1, range_2, distance, in_range",
    [
        (100, 100, 50, True),
        (200, 50, 100, False),
        (50, 200, 100, False),
        (100, None, 80, True),
        (None, None, 100, True),
        (None, 100, 200, False),
    ],
)
def test_transmission_range(range_1, range_2, distance, in_range):

    playground = Playground()

    agent_1 = MockAgent()
    comm_1 = Communicator(transmission_range=range_1)
    agent_1.base.add(comm_1)

    agent_2 = MockAgent()
    comm_2 = Communicator(transmission_range=range_2)
    agent_2.base.add(comm_2)

    playground.add(agent_1, ((100, 100), 0))
    playground.add(agent_2, ((100 + distance, 100), 0))

    messages = {agent_1: {comm_1: (comm_2, "test")}}
    _, msg, _, _ = playground.step(messages=messages)

    assert comm_1.in_transmission_range(comm_2) == in_range

    if in_range:
        assert msg[agent_2][comm_2] == (comm_1, "test")
    else:
        assert msg[agent_2] == {}


def test_directed_broadcast():

    playground = Playground()

    agent_1 = MockAgent()
    comm_1 = Communicator()
    agent_1.base.add(comm_1)
    playground.add(agent_1, ((100, 100), 0))

    agent_2 = MockAgent()
    comm_2 = Communicator()
    agent_2.base.add(comm_2)
    playground.add(agent_2, ((200, 100), 0))

    agent_3 = MockAgent()
    comm_3 = Communicator()
    agent_3.base.add(comm_3)
    playground.add(agent_3, ((100, 200), 0))

    agent_4 = MockAgent()
    comm_4 = Communicator()
    agent_4.base.add(comm_4)
    playground.add(agent_4, ((200, 200), 0))

    # Directed message
    msg_to_single_agent = {agent_1: {comm_1: (comm_2, "test")}}
    playground.step(messages=msg_to_single_agent)

    assert not comm_1.received_messages
    assert comm_2.received_messages == [(comm_1, "test")]
    assert not comm_3.received_messages
    assert not comm_4.received_messages

    # No message, verify receivers are empty
    playground.step()
    assert not comm_1.received_messages
    assert not comm_2.received_messages
    assert not comm_3.received_messages
    assert not comm_4.received_messages

    # Broadcast message
    msg_to_all_agents = {agent_1: {comm_1: (None, "test")}}
    playground.step(messages=msg_to_all_agents)
    assert not comm_1.received_messages
    assert comm_2.received_messages == [(comm_1, "test")]
    assert comm_3.received_messages == [(comm_1, "test")]
    assert comm_4.received_messages == [(comm_1, "test")]


def test_capacity():

    playground = Playground()

    agent_1 = MockAgent()
    comm_1 = LimitedCommunicator(capacity=1)
    agent_1.base.add(comm_1)
    playground.add(agent_1, ((100, 100), 0))

    agent_2 = MockAgent()
    comm_2 = LimitedCommunicator(capacity=2)
    agent_2.base.add(comm_2)
    playground.add(agent_2, ((180, 100), 0))

    agent_3 = MockAgent()
    comm_3 = LimitedCommunicator(capacity=3)
    agent_3.base.add(comm_3)
    playground.add(agent_3, ((200, 120), 0))

    agent_4 = MockAgent()
    comm_4 = LimitedCommunicator(capacity=2)
    agent_4.base.add(comm_4)
    playground.add(agent_4, ((100, 200), 0))

    # Broadcast message
    msg_to_all_agents = {
        agent_1: {comm_1: (None, "test_1")},
        agent_2: {comm_2: (None, "test_2")},
        agent_3: {comm_3: (None, "test_3")},
        agent_4: {comm_4: (None, "test_4")},
    }

    playground.step(messages=msg_to_all_agents)

    # Assert correct message length
    assert len(comm_1.received_messages) == 1
    assert len(comm_2.received_messages) == 2
    assert len(comm_3.received_messages) == 3
    assert len(comm_4.received_messages) == 2

    # Assert priority is given to comm that are closer
    assert comm_1.received_messages == [(comm_2, "test_2")]
    assert comm_2.received_messages == [(comm_3, "test_3"), (comm_1, "test_1")]
    assert comm_3.received_messages == [
        (comm_2, "test_2"),
        (comm_1, "test_1"),
        (comm_4, "test_4"),
    ]
