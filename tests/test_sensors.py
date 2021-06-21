from src.simple_playgrounds import RandomContinuous
from src.simple_playgrounds import HeadAgent
from src.simple_playgrounds import RgbCamera
from src.simple_playgrounds import Engine
from src.simple_playgrounds import Teleports


def test_sensor_without_params(any_sensor, pg_cls):

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

    playground = pg_cls()
    playground.add_agent(agent)

    engine = Engine(playground, time_limit=100)
    engine.run()

    playground.remove_agent(agent)
    playground.reset()


def test_ray_sensors(ray_sensor, resolution, fov, obs_range, pg_cls):

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

    playground = pg_cls()
    playground.add_agent(agent)

    engine = Engine(playground, time_limit=100)
    engine.run()

    playground.remove_agent(agent)
    playground.reset()


def test_rgb_on_teleports(base_forward_agent):

    agent = base_forward_agent

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
