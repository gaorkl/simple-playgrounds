from simple_playgrounds.agents.sensors import RgbCamera, GreyCamera, Lidar,\
    Touch, SemanticRay, SemanticCones, TopdownSensor, BlindCamera
from simple_playgrounds.playgrounds.collection.test.test_scene_elements import Basics, Teleports, Interactives

from simple_playgrounds.agents.parts.controllers import Random
from simple_playgrounds.agents import BaseAgent
from simple_playgrounds.agents.parts import ForwardPlatform
from simple_playgrounds import Engine


def run_experiment_on_sensor(**sensor_config):

    agent = BaseAgent(controller=Random(), interactive=True, platform=ForwardPlatform)

    for sens in [RgbCamera,
                 GreyCamera,
                 BlindCamera,
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

    for pg_class in [Basics, Teleports, Interactives, ]:
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

    for resolution in [2, 16]:

        for range_sensor in [2, 100]:

            for fov in [2, 180, 360, 380]:

                run_experiment_on_sensor(resolution=resolution, max_range=range_sensor, fov=fov)


def test_rgb_on_teleports():

    agent = BaseAgent(controller=Random(), interactive=True, platform=ForwardPlatform)

    agent.add_sensor(RgbCamera(anchor=agent.base_platform,
                              invisible_elements=agent.parts,
                              ))

    playground = Teleports()
    playground.add_agent(agent)

    engine = Engine(playground, time_limit=10000)
    engine.run()

    assert 0 < agent.position[0] < playground.size[0]
    assert 0 < agent.position[1] < playground.size[1]

    playground.remove_agent(agent)
    playground.reset()
