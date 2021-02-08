
from simple_playgrounds.agents.sensors import *

from simple_playgrounds.agents.controllers import Random
from simple_playgrounds.agents import BaseInteractiveAgent
from simple_playgrounds import Engine


from simple_playgrounds.playgrounds.collection.test import *

# Add/remove agent from a playground


# Run all test playgrounds with basic non-interactive agent
def test_camera_sensors():

    agent = BaseInteractiveAgent(controller=Random())

    for resolution in [5, 16]:

        for range_sensor in [5, 16]:

            for fov in [2, 30, 90, 180, 360, 380]:

                for sens in [RgbCamera, GreyCamera, Lidar, Touch, SemanticRay, SemanticCones, TopdownSensor]:

                    agent.add_sensor(sens(anchor=agent.base_platform, invisible_elements=agent.parts,
                                     resolution=resolution, range=range_sensor, fov=fov))

    for pg_class in PlaygroundRegister.filter('test'):
        pg = pg_class()
        pg.add_agent(agent)

        print('Starting testing of ', pg_class.__name__)

        engine = Engine(pg, time_limit=100)
        engine.run()

        assert 0 < agent.position[0] < pg.size[0]
        assert 0 < agent.position[1] < pg.size[1]

        pg.remove_agent(agent)
        pg.reset()
