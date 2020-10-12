
from simple_playgrounds.entities.agents.sensors import *

from simple_playgrounds.controllers import Random
from simple_playgrounds.entities.agents import BaseInteractiveAgent
from simple_playgrounds import Engine


from simple_playgrounds.playgrounds.collection.test import *

# Add/remove agent from a playground


# Run all test playgrounds with basic non-interactive agent
def test_sensors_on_all_test_playgrounds():

    agent = BaseInteractiveAgent(controller=Random())

    agent.add_sensor(
        RgbSensor(name='rgb_1', anchor=agent.base_platform, invisible_elements=agent.parts, resolution=128,
                  range=300))
    agent.add_sensor(TouchSensor(name='touch_1', anchor=agent.base_platform))
    agent.add_sensor(GreySensor(name='grey_1', anchor=agent.base_platform))
    agent.add_sensor(DepthSensor(name='depth_1', anchor=agent.base_platform))
    agent.add_sensor(
        ProximitySensor(name='test_1', anchor=agent.base_platform,
                            fov=180, range=100, number=30))
    agent.add_sensor(TopdownSensor(name='td_1', anchor=agent.base_platform,
                                      range=100, only_front=True))

    agent.add_sensor(LidarRays(name='lidar', anchor=agent.base_platform,
                                   fov=180, range=200, number_rays=100,
                                  remove_occluded=True, allow_duplicates=True))

    agent.add_sensor(LidarCones(name='lidar', anchor=agent.base_platform,
                                   fov=180, range=100, number_cones=10,
                                   resolution=30,
                                   remove_occluded=True, allow_duplicates=True))

    for pg_class in PlaygroundRegister.filter('test'):
        pg = pg_class()

        pg.add_agent(agent)

        print('Starting testing of ', pg_class.__name__)

        engine = Engine(pg, time_limit=100, replay=False)
        engine.run()

        assert 0 < agent.position[0] < pg.size[0]
        assert 0 < agent.position[1] < pg.size[1]

        pg.remove_agent(agent)
        pg.reset()
#
# def test_noisy_sensors_on_all_test_playgrounds():
#     agent = BaseInteractiveAgent(controller=Random())
#
#     sensor = RgbSensor(name='rgb_1', anchor=agent.base_platform, resolution=128,
#                   range=300)
#     agent.add_sensor( NoisySensor(sensor, 'deadpixel', proba=0.01, dynamic=True) )
#
#     sensor = TouchSensor(name='touch_1', anchor=agent.base_platform)
#     agent.add_sensor(NoisySensor(sensor, 'deadpixel', proba=0.01, dynamic=True))
#
#     sensor = GreySensor(name='grey_1', anchor=agent.base_platform)
#     agent.add_sensor(NoisySensor(sensor, 'deadpixel', proba=0.01, dynamic=True))
#
#     sensor = DepthSensor(name='depth_1', anchor=agent.base_platform)
#     agent.add_sensor(NoisySensor(sensor, 'deadpixel', proba=0.01, dynamic=True))
#
#     sensor = ProximitySensor(name='test_1', anchor=agent.base_platform,
#                             fov=180, range=100, number=30)
#     agent.add_sensor(NoisySensor(sensor, 'deadpixel', proba=0.01, dynamic=True))
#
#     sensor = TopdownSensor(name='td_1', anchor=agent.base_platform,
#                                    range=100, only_front=True)
#     agent.add_sensor(NoisySensor(sensor, 'deadpixel', proba=0.01, dynamic=True))
#
#
#     for pg_class in PlaygroundRegister.filter('test'):
#         pg = pg_class()
#
#         pg.add_agent(agent)
#
#         print('Starting testing of ', pg_class.__name__)
#
#         engine = Engine(pg, time_limit=100, replay=False)
#         engine.run()
#
#         assert 0 < agent.position[0] < pg.size[0]
#         assert 0 < agent.position[1] < pg.size[1]
#
#         pg.remove_agent(agent)
#         pg.reset()

