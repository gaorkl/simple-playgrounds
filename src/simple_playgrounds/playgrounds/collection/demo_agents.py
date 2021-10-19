import simple_playgrounds.agents.sensors as sensors
from simple_playgrounds.agents.agents import HeadAgent
from simple_playgrounds.agents.parts.controllers import Keyboard


def get_all_sensor_agent():
    agent = HeadAgent(controller=Keyboard(), lateral=True, interactive=True)
    sensor_list = []

    sensor_list.append(
        sensors.RgbCamera(
            agent.head,
            invisible_elements=agent.parts,
            fov=180,
            resolution=64,
            max_range=500))

    sensor_list.append(
        sensors.GreyCamera(
            agent.head,
            invisible_elements=agent.parts,
            fov=180,
            resolution=64,
            max_range=500))

    sensor_list.append(
        sensors.Lidar(
            agent.base_platform,
            normalize=False,
            invisible_elements=agent.parts,
            fov=180,
            resolution=128,
            max_range=400))

    sensor_list.append(
        sensors.Proximity(
            agent.base_platform,
            normalize=False,
            invisible_elements=agent.parts,
            fov=100,
            resolution=64,
            max_range=400))

    sensor_list.append(
        sensors.Touch(
            agent.base_platform,
            normalize=True,
            invisible_elements=agent.parts))

    sensor_list.append(
        sensors.SemanticRay(
            agent.base_platform,
            invisible_elements=agent.parts,
            remove_duplicates=False,
            fov=90))

    sensor_list.append(
        sensors.SemanticCones(
            agent.base_platform,
            invisible_elements=agent.parts,
            normalize=True,
            remove_duplicates=False))

    sensor_list.append(
        sensors.TopdownSensor(
            agent.head,
            invisible_elements=agent.parts,
            normalize=True,
            only_front=True,
            fov=180))

    sensor_list.append(
        sensors.FullPlaygroundSensor(agent.base_platform, resolution=64))

    sensor_list.append(
        sensors.semantic_sensors.PerfectLidar(agent.base_platform))

    sensor_list.append(
        sensors.semantic_sensors.PerfectLidar(agent.base_platform, fov=180))

    for sensor in sensor_list:
        agent.add_sensor(sensor)

    return agent
