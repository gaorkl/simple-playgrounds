import numpy as np

from simple_playgrounds.engine import Engine
from simple_playgrounds.playground.layouts import SingleRoom
from simple_playgrounds.agent.agents import BaseAgent
from simple_playgrounds.agent.controllers import External

from simple_playgrounds.device.communication import CommunicationDevice
from simple_playgrounds.element.elements.modifier import CommunicationDisabler, SensorDisabler

from simple_playgrounds.device.sensors.robotic import Lidar, RgbCamera
from simple_playgrounds.device.sensors.semantic import SemanticRay
from simple_playgrounds.device.sensor import SensorDevice


def test_disable_communication_sender():

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

    comm_1 = CommunicationDevice(agent_1.base_platform)
    agent_1.add_communication(comm_1)

    comm_2 = CommunicationDevice(agent_2.base_platform)
    agent_2.add_communication(comm_2)

    playground.add_agent(agent_1, ((100, 100), 0))
    playground.add_agent(agent_2, ((200, 100), 0))

    disabler = CommunicationDisabler()
    playground.add_element(disabler, ((100, 100), 0))

    assert agent_1.communication
    assert agent_2.communication

    engine = Engine(playground)

    messages = [(comm_1, 'test', comm_2)]
    engine.step(messages=messages)

    assert comm_1._disabled
    assert comm_2.received_message == []


def test_disable_communication_receiver():

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

    comm_1 = CommunicationDevice(agent_1.base_platform)
    agent_1.add_communication(comm_1)

    comm_2 = CommunicationDevice(agent_2.base_platform)
    agent_2.add_communication(comm_2)

    playground.add_agent(agent_1, ((100, 100), 0))
    playground.add_agent(agent_2, ((200, 100), 0))

    disabler = CommunicationDisabler()
    playground.add_element(disabler, ((200, 100), 0))

    assert agent_1.communication
    assert agent_2.communication

    engine = Engine(playground)

    messages = [(comm_1, 'test', comm_2)]
    engine.step(messages=messages)

    assert not comm_1._disabled
    assert comm_2._disabled

    assert comm_2.received_message == []


def test_disable_all_sensors():

    playground = SingleRoom(size=(300, 200))

    agent_1 = BaseAgent(
        controller=External(),
        interactive=False,
        rotate=False,
        lateral=False
    )

    sensor_1 = RgbCamera(agent_1.base_platform, invisible_elements=agent_1.parts)
    sensor_2 = Lidar(agent_1.base_platform, invisible_elements=agent_1.parts)
    sensor_3 = SemanticRay(agent_1.base_platform, invisible_elements=agent_1.parts)

    agent_1.add_sensor(sensor_1)
    agent_1.add_sensor(sensor_2)
    agent_1.add_sensor(sensor_3)

    playground.add_agent(agent_1, ((100, 100), 0))

    disabler = SensorDisabler(disabled_sensor_types=SensorDevice)
    playground.add_element(disabler, ((100, 100), 0))

    engine = Engine(playground)
    engine.step()
    engine.update_observations()

    for sensor in [sensor_1, sensor_2, sensor_3]:
        assert sensor._disabled

        if isinstance(sensor.sensor_values, np.ndarray):
            assert np.all(sensor.sensor_values == sensor._get_null_sensor())

        else:
            assert sensor.sensor_values == sensor._get_null_sensor()


def test_one_sensor():

    playground = SingleRoom(size=(300, 200))

    agent_1 = BaseAgent(
        controller=External(),
        interactive=False,
        rotate=False,
        lateral=False
    )

    sensor_1 = RgbCamera(anchor=agent_1.base_platform, invisible_elements=agent_1.parts, max_range=400)
    sensor_2 = Lidar(anchor=agent_1.base_platform, invisible_elements=agent_1.parts, max_range=400)
    sensor_3 = SemanticRay(anchor=agent_1.base_platform, invisible_elements=agent_1.parts, max_range=400)

    agent_1.add_sensor(sensor_1)
    agent_1.add_sensor(sensor_2)
    agent_1.add_sensor(sensor_3)

    playground.add_agent(agent_1, ((100, 100), 0))

    disabler = SensorDisabler(disabled_sensor_types=RgbCamera)
    playground.add_element(disabler, ((100, 100), 0))

    engine = Engine(playground)
    engine.step()
    engine.update_observations()

    for sensor in [sensor_1, sensor_2, sensor_3]:

        if isinstance(sensor, RgbCamera):
            assert sensor._disabled
            assert np.all(sensor.sensor_values == sensor._get_null_sensor())

        else:
            assert not sensor._disabled
            if isinstance(sensor.sensor_values, np.ndarray):
                assert not np.all(sensor.sensor_values == sensor._get_null_sensor())

            else:
                assert not sensor.sensor_values == sensor._get_null_sensor()


def test_list_sensors():

    playground = SingleRoom(size=(300, 200))

    agent_1 = BaseAgent(
        controller=External(),
        interactive=False,
        rotate=False,
        lateral=False
    )

    sensor_1 = RgbCamera(anchor=agent_1.base_platform, invisible_elements=agent_1.parts, range=400)
    sensor_2 = Lidar(anchor=agent_1.base_platform, invisible_elements=agent_1.parts, range=400)
    sensor_3 = SemanticRay(anchor=agent_1.base_platform, invisible_elements=agent_1.parts, range=400)

    agent_1.add_sensor(sensor_1)
    agent_1.add_sensor(sensor_2)
    agent_1.add_sensor(sensor_3)

    playground.add_agent(agent_1, ((100, 100), 0))

    disabler = SensorDisabler(disabled_sensor_types=[RgbCamera, SemanticRay])
    playground.add_element(disabler, ((100, 100), 0))

    engine = Engine(playground)
    engine.step()
    engine.update_observations()

    for sensor in [sensor_1, sensor_2, sensor_3]:

        if isinstance(sensor, RgbCamera):
            assert sensor._disabled
            assert np.all(sensor.sensor_values == sensor._get_null_sensor())

        elif isinstance(sensor, SemanticRay):
            assert sensor._disabled
            assert sensor.sensor_values == sensor._get_null_sensor()

        else:

            assert not sensor._disabled

            if isinstance(sensor.sensor_values, np.ndarray):
                assert not np.all(sensor.sensor_values == sensor._get_null_sensor())

            else:
                assert not sensor.sensor_values == sensor._get_null_sensor()
