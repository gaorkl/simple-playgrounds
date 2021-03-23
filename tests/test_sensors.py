from simple_playgrounds.agents.sensors import RgbCamera, GreyCamera, Lidar,\
    Touch, SemanticRay, SemanticCones, TopdownSensor
from simple_playgrounds.agents.sensors.sensor import Sensor

from simple_playgrounds.agents.controllers import Random
from simple_playgrounds.agents import BaseAgent
from simple_playgrounds.agents.parts import ForwardPlatform
from simple_playgrounds import Engine

from simple_playgrounds.playground import PlaygroundRegister


def run_experiment_on_sensor(**sensor_config):

    agent = BaseAgent(controller=Random(), interactive=True, platform=ForwardPlatform)

    for sens in [RgbCamera,
                 GreyCamera,
                 Lidar,
                 Touch,
                 SemanticRay,
                 SemanticCones,
                 TopdownSensor]:
        agent.add_sensor(sens(anchor=agent.base_platform,
                              invisible_elements=agent.parts,
                              **sensor_config
                              ))

    print('Testing of sensor params ', sensor_config)

    for pg_name, pg_class in PlaygroundRegister.playgrounds['test'].items():
        playground = pg_class()
        playground.add_agent(agent)

        print('.... on playground ', pg_class.__name__)

        engine = Engine(playground, time_limit=100)
        engine.run()

        assert 0 < agent.position[0] < playground.size[0]
        assert 0 < agent.position[1] < playground.size[1]

        playground.remove_agent(agent)
        playground.reset()


# Run all test playgrounds with basic non-interactive agent
def test_default_sensors():

    run_experiment_on_sensor()


def test_parameter_sensors():

    for resolution in [2, 16, 32]:

        for range_sensor in [2, 100, 500]:

            for fov in [2, 30, 90, 180, 360, 380]:

                run_experiment_on_sensor(resolution=resolution, max_range=range_sensor, fov=fov)

def test_rgb_on_teleports():

    agent = BaseAgent(controller=Random(), interactive=True, platform=ForwardPlatform)

    agent.add_sensor(RgbCamera(anchor=agent.base_platform,
                              invisible_elements=agent.parts,
                              ))

    from simple_playgrounds.playgrounds.collection import Teleports
    playground = Teleports()
    playground.add_agent(agent)

    engine = Engine(playground, time_limit=10000)
    engine.run()

    assert 0 < agent.position[0] < playground.size[0]
    assert 0 < agent.position[1] < playground.size[1]

    playground.remove_agent(agent)
    playground.reset()