
from simple_playgrounds.agents.sensors import RgbCamera, GreyCamera, Lidar,\
    Touch, SemanticRay, SemanticCones, TopdownSensor

from simple_playgrounds.agents.controllers import Random
from simple_playgrounds.agents import BaseAgent
from simple_playgrounds.agents.parts import ForwardPlatform
from simple_playgrounds import Engine

from simple_playgrounds.playground import PlaygroundRegister

# Add/remove agent from a playground


# Run all test playgrounds with basic non-interactive agent
def test_camera_sensors():

    agent = BaseAgent(controller=Random(), interactive=True, platform=ForwardPlatform)

    for resolution in [5, 16]:

        for range_sensor in [5, 16]:

            for fov in [2, 30, 90, 180, 360, 380]:

                for sens in [RgbCamera,
                             GreyCamera,
                             Lidar,
                             Touch,
                             SemanticRay,
                             SemanticCones,
                             TopdownSensor]:

                    agent.add_sensor(sens(anchor=agent.base_platform,
                                          invisible_elements=agent.parts,
                                          resolution=resolution, max_range=range_sensor, fov=fov))

    for pg_name, pg_class in PlaygroundRegister.playgrounds['test'].items():
        playground = pg_class()
        playground.add_agent(agent)

        print('Starting testing of ', pg_class.__name__)

        engine = Engine(playground, time_limit=100)
        engine.run()

        assert 0 < agent.position[0] < playground.size[0]
        assert 0 < agent.position[1] < playground.size[1]

        playground.remove_agent(agent)
        playground.reset()
