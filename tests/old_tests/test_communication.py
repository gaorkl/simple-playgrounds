import pytest

from simple_playgrounds.engine import Engine
from simple_playgrounds.playground.layouts import SingleRoom
from simple_playgrounds.agent.agents import BaseAgent
from simple_playgrounds.agent.controllers import External

from simple_playgrounds.device.communication import CommunicationDevice


def test_equip_communication(comm_radius):

    playground = SingleRoom(size=(300, 200))

    agent_1 = BaseAgent(
        controller=External(),
        interactive=False,
        rotate=False,
        lateral=False
    )

    agent_2 = BaseAgent(
        controller=External(),
        interactive=False,
        rotate=False,
        lateral=False
    )

    comm_1 = CommunicationDevice(agent_1.base_platform, comm_radius)
    agent_1.add_communication(comm_1)

    playground.add_agent(agent_1, ((100, 100), 0))
    playground.add_agent(agent_2, ((200, 100), 0))

    assert agent_1.communication
    assert not agent_2.communication


@pytest.mark.parametrize(
    "range_1, range_2, distance, in_range",
    [(100, 100, 50, True),
     (200, 50, 100, False),
     (50, 200, 100, False),
     (100, None, 80, True),
     (None, None, 100, True),
     (None, 100, 200, False)
     ]
)
def test_transmission_range(range_1, range_2, distance, in_range):

    playground = SingleRoom(size=(300, 200))

    agent_1 = BaseAgent(
        controller=External(),
        interactive=False,
        rotate=False,
        lateral=False
    )

    agent_2 = BaseAgent(
        controller=External(),
        interactive=False,
        rotate=False,
        lateral=False
    )

    comm_1 = CommunicationDevice(agent_1.base_platform, range_1)
    agent_1.add_communication(comm_1)

    comm_2 = CommunicationDevice(agent_2.base_platform, range_2)
    agent_2.add_communication(comm_2)

    playground.add_agent(agent_1, ((100, 100), 0))
    playground.add_agent(agent_2, ((100+distance, 100), 0))

    assert agent_1.communication
    assert agent_2.communication

    assert comm_1.in_transmission_range(comm_2) is in_range
    assert comm_2.in_transmission_range(comm_1) is in_range

    engine = Engine(playground)

    messages = [ (comm_1, 'test', comm_2) ]
    engine.step(messages=messages)

    if in_range:
        assert comm_2.received_message == [(comm_1, 'test')]
    else:
        assert comm_2.received_message == []


def test_directed_broadcast():
    playground = SingleRoom(size=(300, 200))

    agent_1 = BaseAgent(
        controller=External(),
        interactive=False,
        rotate=False,
        lateral=False
    )

    agent_2 = BaseAgent(
        controller=External(),
        interactive=False,
        rotate=False,
        lateral=False
    )

    agent_3 = BaseAgent(
        controller=External(),
        interactive=False,
        rotate=False,
        lateral=False
    )

    agent_4 = BaseAgent(
        controller=External(),
        interactive=False,
        rotate=False,
        lateral=False
    )

    comm_1 = CommunicationDevice(agent_1.base_platform, receiver_capacity=1)
    agent_1.add_communication(comm_1)

    comm_2 = CommunicationDevice(agent_2.base_platform, receiver_capacity=2)
    agent_2.add_communication(comm_2)

    comm_3 = CommunicationDevice(agent_3.base_platform, receiver_capacity=3)
    agent_3.add_communication(comm_3)

    comm_4 = CommunicationDevice(agent_4.base_platform, receiver_capacity=4)
    agent_4.add_communication(comm_4)

    playground.add_agent(agent_1, ((100, 100), 0))
    playground.add_agent(agent_2, ((180, 100), 0))
    playground.add_agent(agent_3, ((200, 120), 0))
    playground.add_agent(agent_4, ((100, 200), 0))

    engine = Engine(playground)

    # Directed message
    msg_to_single_agent = [(comm_1, 'test', comm_2)]
    engine.step(messages=msg_to_single_agent)
    assert comm_1.received_message == []
    assert comm_2.received_message == [(comm_1, 'test')]
    assert comm_3.received_message == []
    assert comm_4.received_message == []

    # No message, verify receivers are empty
    engine.step()
    assert comm_1.received_message == []
    assert comm_2.received_message == []
    assert comm_3.received_message == []
    assert comm_4.received_message == []

    # Broadcast message
    msg_to_all_agents = [(comm_1, 'test', None)]
    engine.step(messages=msg_to_all_agents)
    assert comm_1.received_message == []
    assert comm_2.received_message == [(comm_1, 'test')]
    assert comm_3.received_message == [(comm_1, 'test')]
    assert comm_4.received_message == [(comm_1, 'test')]


def test_capacity():
    playground = SingleRoom(size=(300, 200))

    agent_1 = BaseAgent(
        controller=External(),
        interactive=False,
        rotate=False,
        lateral=False
    )

    agent_2 = BaseAgent(
        controller=External(),
        interactive=False,
        rotate=False,
        lateral=False
    )

    agent_3 = BaseAgent(
        controller=External(),
        interactive=False,
        rotate=False,
        lateral=False
    )

    agent_4 = BaseAgent(
        controller=External(),
        interactive=False,
        rotate=False,
        lateral=False
    )

    comm_1 = CommunicationDevice(agent_1.base_platform, receiver_capacity=1)
    agent_1.add_communication(comm_1)

    comm_2 = CommunicationDevice(agent_2.base_platform, receiver_capacity=2)
    agent_2.add_communication(comm_2)

    comm_3 = CommunicationDevice(agent_3.base_platform, receiver_capacity=3)
    agent_3.add_communication(comm_3)

    comm_4 = CommunicationDevice(agent_4.base_platform, receiver_capacity=2)
    agent_4.add_communication(comm_4)

    playground.add_agent(agent_1, ((100, 100), 0))
    playground.add_agent(agent_2, ((180, 100), 0))
    playground.add_agent(agent_3, ((200, 120), 0))
    playground.add_agent(agent_4, ((100, 200), 0))

    engine = Engine(playground)

    # Broadcast message
    msg_to_all_agents = [(comm_1, 'test_1', None),
                         (comm_2, 'test_2', None),
                         (comm_3, 'test_3', None),
                         (comm_4, 'test_4', None),
                         ]

    engine.step(messages=msg_to_all_agents)

    # Assert correct message length
    assert len(comm_1.received_message) == 1
    assert len(comm_2.received_message) == 2
    assert len(comm_3.received_message) == 3
    assert len(comm_4.received_message) == 2

    # Assert priority is given to comm that are closer
    assert comm_1.received_message == [(comm_2, 'test_2')]
    assert comm_2.received_message == [(comm_3, 'test_3'), (comm_1, 'test_1')]
    assert comm_3.received_message == [(comm_2, 'test_2'), (comm_1, 'test_1'), (comm_4, 'test_4')]


