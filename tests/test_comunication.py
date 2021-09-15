import pytest

from simple_playgrounds.engine import Engine
from simple_playgrounds.playgrounds.layouts import SingleRoom
from simple_playgrounds.agents.agents import BaseAgent
from simple_playgrounds.agents.parts.controllers import External

from simple_playgrounds.agents.communication import CommunicationDevice


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

    assert agent_1.can_communicate
    assert not agent_2.can_communicate


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

    assert agent_1.can_communicate
    assert agent_2.can_communicate

    assert comm_1.in_transmission_range(comm_2) is in_range
    assert comm_2.in_transmission_range(comm_1) is in_range

    engine = Engine(playground)

    messages = [ (comm_1, 'test', comm_2) ]
    engine.step(messages=messages)

    if in_range:
        assert comm_2.received_message == [(comm_1, 'test')]
    else:
        assert comm_2.received_message == []


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

    comm_4 = CommunicationDevice(agent_4.base_platform, receiver_capacity=4)
    agent_4.add_communication(comm_4)

    playground.add_agent(agent_1, ((100, 100), 0))
    playground.add_agent(agent_2, ((180, 100), 0))
    playground.add_agent(agent_3, ((200, 120), 0))
    playground.add_agent(agent_4, ((100, 200), 0))

    assert agent_1.can_communicate
    assert agent_2.can_communicate

    assert comm_1.in_transmission_range(comm_2) is in_range
    assert comm_2.in_transmission_range(comm_1) is in_range

    engine = Engine(playground)

    messages = [(comm_1, 'test', comm_2)]
    engine.step(messages=messages)

    if in_range:
        assert comm_2.received_message == [(comm_1, 'test')]
    else:
        assert comm_2.received_message == []
