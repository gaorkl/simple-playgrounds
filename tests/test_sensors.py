import pytest

from simple_playgrounds.agents.parts.controllers import RandomContinuous
from simple_playgrounds.agents.agents import HeadAgent, BaseAgent
from simple_playgrounds.agents.sensors import RgbCamera, Lidar, Touch, GPS, Velocity
from simple_playgrounds.engine import Engine
from simple_playgrounds.playgrounds.collection.demo_playgrounds import Teleports


def test_sensor_without_params(any_sensor, pg_sensor_class):

    agent = HeadAgent(controller=RandomContinuous(), interactive=True)

    agent.add_sensor(
        any_sensor(
            anchor=agent.head,
            invisible_elements=agent.parts,
        ))

    agent.add_sensor(
        RgbCamera(
            anchor=agent.base_platform,
            min_range=agent.base_platform.radius,
        ))

    playground = pg_sensor_class()
    playground.add_agent(agent)

    engine = Engine(playground, time_limit=1000)
    engine.run()

    playground.remove_agent(agent)
    playground.reset()


def test_ray_sensors(ray_sensor, resolution, fov, obs_range, pg_sensor_class):

    agent = HeadAgent(controller=RandomContinuous(), interactive=True)

    agent.add_sensor(
        ray_sensor(anchor=agent.head,
                   invisible_elements=agent.parts,
                   fov=fov,
                   resolution=resolution,
                   max_range=obs_range))

    agent.add_sensor(
        ray_sensor(anchor=agent.head,
                   min_range=agent.base_platform.radius,
                   fov=fov,
                   resolution=resolution,
                   max_range=obs_range))

    playground = pg_sensor_class()
    playground.add_agent(agent)

    engine = Engine(playground, time_limit=100)
    engine.run()

    playground.remove_agent(agent)
    playground.reset()


def test_rgb_on_teleports(base_forward_agent_random):

    agent = base_forward_agent_random

    agent.add_sensor(
        RgbCamera(
            anchor=agent.base_platform,
            invisible_elements=agent.parts,
        ))

    agent.add_sensor(
        RgbCamera(
            anchor=agent.base_platform,
            min_range=agent.base_platform.radius,
        ))

    playground = Teleports()
    playground.add_agent(agent)

    engine = Engine(playground, time_limit=10000)
    engine.run()

    assert 0 < agent.position[0] < playground.size[0]
    assert 0 < agent.position[1] < playground.size[1]

    playground.remove_agent(agent)
    playground.reset()


def test_pose_sensors(pg_sensor_class):

    agent = HeadAgent(controller=RandomContinuous(), interactive=True)

    agent.add_sensor(GPS(anchor=agent.head))
    agent.add_sensor(Velocity(anchor=agent.head))

    playground = pg_sensor_class()
    playground.add_agent(agent)

    engine = Engine(playground, time_limit=1000)
    engine.run()

    head = agent.head

    gps_values = agent.sensors[0].sensor_values
    assert head.position[0] == gps_values[0]
    assert head.position[1] == gps_values[1]
    assert head.angle == gps_values[2]

    vel_values = agent.sensors[1].sensor_values
    assert head.velocity[0] == vel_values[0]
    assert head.velocity[1] == vel_values[1]
    assert head.angular_velocity == vel_values[2]

    playground.remove_agent(agent)
    playground.reset()


def test_max_sensors(pg_sensor_class):

    # Test adding multiple sensors to agent
    agent = HeadAgent(controller=RandomContinuous(), interactive=True)
    for i in range(60):
        agent.add_sensor(
            RgbCamera(anchor=agent.head,
                      invisible_elements=agent.parts,
                      )
        )
    playground = pg_sensor_class()
    playground.add_agent(agent)

    # Test adding multiple sensors to agent, with min range
    agent = HeadAgent(controller=RandomContinuous(), interactive=True)
    for i in range(60):
        agent.add_sensor(
            RgbCamera(anchor=agent.head,
                      min_range=30,
                      )
        )
    playground = pg_sensor_class()
    playground.add_agent(agent)

    # Test adding multiple sensors to basic agent, with min_range not set.
    agent = BaseAgent(controller=RandomContinuous(), interactive=True)
    for i in range(60):
        agent.add_sensor(
            RgbCamera(anchor=agent.base_platform,
                      )
        )
    playground = pg_sensor_class()
    playground.add_agent(agent)

    # Test adding multiple agents
    playground = pg_sensor_class()
    for i in range(40):
        agent = HeadAgent(controller=RandomContinuous(), interactive=True)
        agent.add_sensor(
            RgbCamera(anchor=agent.head,
                      invisible_elements=agent.parts,
                      )
        )

        playground.add_agent(agent)

    agent = HeadAgent(controller=RandomContinuous(), interactive=True)
    agent.add_sensor(
        RgbCamera(anchor=agent.head,
                  invisible_elements=agent.parts,
                  )
    )

    # Test adding multiple sensors to multiple agents, with min range
    for n_agent in range(40):

        agent = HeadAgent(controller=RandomContinuous(), interactive=True)

        agent.add_sensor(
            RgbCamera(anchor=agent.head,
                      min_range=agent.base_platform.radius,
                      )
        )
        agent.add_sensor(
            Lidar(anchor=agent.head,
                  min_range=agent.base_platform.radius,
                  )
        )
        agent.add_sensor(
            Touch(anchor=agent.head,
                  min_range=agent.base_platform.radius,
                  )
        )

        playground.add_agent(agent)

