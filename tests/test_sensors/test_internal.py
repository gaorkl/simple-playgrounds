import math
import numpy as np

from simple_playgrounds.agents.parts.controllers import External, RandomContinuous
from simple_playgrounds.agents.agents import BaseAgent, HeadAgent
from simple_playgrounds.agents.sensors import Position, Velocity, Time
from simple_playgrounds.engine import Engine
from simple_playgrounds.playgrounds import SingleRoom


def test_normalize_position_sensor():

    agent = BaseAgent(controller=External(), rotate=True)

    pos = Position(anchor=agent.base_platform, normalize=False)
    pos_norm = Position(anchor=agent.base_platform, normalize=True)
    agent.add_sensor(pos)
    agent.add_sensor(pos_norm)

    playground = SingleRoom((400, 400))
    playground.add_agent(agent, initial_coordinates=((100, 200), math.pi))

    engine = Engine(playground, time_limit=1000)
    engine.update_observations()

    assert np.all( pos.sensor_values == np.asarray( (100, 200, math.pi) ) )
    assert np.all( pos_norm.sensor_values == np.asarray( (0.25, 0.5, 0.5) ) )


def test_pose_sensors(pg_sensor_class):

    agent = HeadAgent(controller=RandomContinuous(), interactive=True)

    agent.add_sensor(Position(anchor=agent.head))
    agent.add_sensor(Velocity(anchor=agent.head))

    playground = pg_sensor_class()
    playground.add_agent(agent)

    engine = Engine(playground, time_limit=1000)
    engine.run()

    head = agent.head

    pos_values = agent.sensors[0].sensor_values
    assert head.position[0] == pos_values[0]
    assert head.position[1] == pos_values[1]
    assert head.angle == pos_values[2]

    vel_values = agent.sensors[1].sensor_values
    assert head.velocity[0] == vel_values[0]
    assert head.velocity[1] == vel_values[1]
    assert head.angular_velocity == vel_values[2]

    playground.remove_agent(agent)
    playground.reset()


def test_time_sensor(pg_sensor_class):

    agent = HeadAgent(controller=RandomContinuous(), interactive=True)

    agent.add_sensor(Time(anchor=agent.head))

    playground = pg_sensor_class()
    playground.add_agent(agent)

    engine = Engine(playground, time_limit=100)

    for _ in range(100):
        engine.run(1)
        time_value = agent.sensors[0].sensor_values
        assert engine.elapsed_time == time_value

    engine.reset()
    engine.run(1)
    time_value = agent.sensors[0].sensor_values
    assert 1 == time_value

    playground.remove_agent(agent)
    playground.reset()
