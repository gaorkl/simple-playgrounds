
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

        engine = Engine(pg, time_limit=100, replay=False)
        engine.run()

        assert 0 < agent.position[0] < pg.size[0]
        assert 0 < agent.position[1] < pg.size[1]

        pg.remove_agent(agent)
        pg.reset()
#
#
#
# # Test angles visual
# def test_angle_visual_sensors():
#
#     from simple_playgrounds.playgrounds import SingleRoom
#
#
#     angles = [ a * 2*math.pi/12 for a in range(13)]
#
#     for angle in angles:
#
#         agent = BaseInteractiveAgent(initial_position=[100,100, angle], controller = Random())
#
#         agent.add_sensor(
#             RgbCamera(name='rgb_1', anchor=agent.base_platform, invisible_elements=agent.parts, resolution=128,
#                       range=300))
#
#         pg = SingleRoom((200, 200))
#
#         pg.add_agent(agent)
#
#         print('Starting testing of angle', angle)
#
#         engine = Engine(pg, time_limit=100, replay=False)
#         engine.run()
#
#         assert 0 < agent.position[0] < pg.size[0]
#         assert 0 < agent.position[1] < pg.size[1]
#
#         pg.remove_agent(agent)
#         pg.reset()
#
#
# def test_geometric_sensors():
#
#     agent = BaseInteractiveAgent(controller=Random())
#
#     angles = [ a * 2*math.pi/12 for a in range(13)]
#
#     for index, angle in enumerate(angles):
#
#         agent.add_sensor(
#             TouchSensor(name='touch_' + str(index), anchor=agent.base_platform, invisible_elements=agent.parts,
#                         resolution=32,
#                         range=5, fov=angle * 180 / math.pi))
#
#         agent.add_sensor(
#         DepthSensor(name='depth' + str(index), anchor=agent.base_platform, invisible_elements=agent.parts,
#                         resolution=32,
#                         range=300, fov=angle * 180 / math.pi))
#
#         agent.add_sensor(
#             ProximitySensor(name='prox_' + str(index), anchor=agent.base_platform, invisible_elements=agent.parts,
#                         resolution=32,
#                         range=300, fov=angle * 180 / math.pi))
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
#
#
# def test_semantic_sensors():
#
#     agent = BaseInteractiveAgent(controller=Random())
#
#     angles = [ a * 2*math.pi/12 for a in range(1,13)]
#
#     for index, angle in enumerate(angles):
#
#         agent.add_sensor(
#             LidarRays(name='rays_' + str(index), anchor=agent.base_platform, invisible_elements=agent.parts,
#                       number_rays=32, range=300, fov=angle * 180 / math.pi))
#
#         agent.add_sensor(
#             LidarCones(name='cones_' + str(index), anchor=agent.base_platform, invisible_elements=agent.parts,
#                        number_cones=16, range=300, fov=angle * 180 / math.pi, resolution = 10))
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