from simple_playgrounds.agents.parts.controllers import RandomContinuous
from simple_playgrounds.agents.agents import HeadAgent
from simple_playgrounds.agents.sensors import RgbCamera
from simple_playgrounds import SPGEngine
from simple_playgrounds.playgrounds.collection import Basics, Teleports, Interactives, ExtraTeleports


def test_sensor_without_params(any_sensor):

    agent = HeadAgent(controller=RandomContinuous(), interactive=True)

    agent.add_sensor(any_sensor(anchor=agent.head,
                                invisible_elements=agent.parts,
                                ))

    agent.add_sensor(RgbCamera(anchor=agent.base_platform,
                               min_range=agent.base_platform.radius,
                               ))

    for pg_class in [Basics, Teleports, Interactives, ]:
        playground = pg_class()
        playground.add_agent(agent)

        engine = SPGEngine(playground, time_limit=100)
        engine.run()

        playground.remove_agent(agent)
        playground.reset()


def test_ray_sensors(ray_sensor, resolution, fov, obs_range):

    agent = HeadAgent(controller=RandomContinuous(), interactive=True)

    agent.add_sensor(ray_sensor(anchor=agent.head,
                                   invisible_elements=agent.parts,
                                   fov=fov,
                                   resolution=resolution,
                                   max_range=obs_range
                                  ))

    agent.add_sensor(ray_sensor(anchor=agent.head,
                                   min_range=agent.base_platform.radius,
                                   fov=fov,
                                   resolution=resolution,
                                   max_range=obs_range
                                   ))

    for pg_class in [Basics, Teleports, Interactives, ]:
        playground = pg_class()
        playground.add_agent(agent)

        engine = SPGEngine(playground, time_limit=100)
        engine.run()

        playground.remove_agent(agent)
        playground.reset()


def test_rgb_on_teleports(base_forward_agent):

    agent = base_forward_agent

    agent.add_sensor(RgbCamera(anchor=agent.base_platform,
                               invisible_elements=agent.parts,
                               ))

    agent.add_sensor(RgbCamera(anchor=agent.base_platform,
                               min_range=agent.base_platform.radius,
                               ))

    playground = ExtraTeleports()
    playground.add_agent(agent)

    engine = SPGEngine(playground, time_limit=10000)
    engine.run()

    assert 0 < agent.position[0] < playground.size[0]
    assert 0 < agent.position[1] < playground.size[1]

    playground.remove_agent(agent)
    playground.reset()
