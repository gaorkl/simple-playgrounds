import math

import arcade.color
import numpy as np
import pytest

from spg.core.playground import Playground
from spg.core.sensor.ray.ray import SIZE_OUTPUT_BUFFER
from tests.mock_agents import DynamicAgent, MockRaySensor
from tests.mock_entities import DynamicElementFromGeometry

coord_center = (0, 0), 0


def test_sensor_interface():
    playground = Playground(size=(500, 200), background=(23, 23, 21))

    agent = DynamicAgent()

    sensor = MockRaySensor(fov=math.pi / 4, max_range=100, resolution=10)
    agent.add(sensor)

    playground.add(agent, coord_center)

    assert playground.ray_compute is not None
    assert len(playground.ray_compute.sensors) == 1
    assert playground.ray_compute.sensors[0] == sensor


@pytest.mark.parametrize("use_shaders", [True, False])
@pytest.mark.parametrize("max_range", [1, 10, 100, 1000])
@pytest.mark.parametrize("resolution", [1, 8, 180])
@pytest.mark.parametrize("fov", [math.pi / 4, math.pi / 3, math.pi / 2])
def test_sensor_parameters(max_range, resolution, fov, use_shaders):
    playground = Playground(
        size=(300, 300), background=arcade.color.DARK_KHAKI, use_shaders=use_shaders
    )

    agent = DynamicAgent()

    sensor = MockRaySensor(fov=fov, max_range=max_range, resolution=resolution)
    agent.add(sensor)

    playground.add(agent, coord_center)

    assert playground.ray_compute is not None
    assert len(playground.ray_compute.sensors) == 1
    assert playground.ray_compute.sensors[0] == sensor

    playground.step(playground.null_action)

    assert sensor.updated

    # test sensor output
    assert sensor.observation.shape == (resolution, SIZE_OUTPUT_BUFFER)
    assert agent in sensor.invisible_entities

    assert np.all(sensor.observation[:, 8] == 0)
    assert np.all(sensor.observation[:, 9] == max_range)

    if agent.radius < max_range < playground.width / 2:
        assert np.all(sensor.observation[:, 10:13] == playground.background[:3])


@pytest.mark.parametrize("fov", [math.pi / 4, math.pi / 3, math.pi / 2])
@pytest.mark.parametrize("resolution", [8, 21])
@pytest.mark.parametrize(
    "color", [arcade.color.AFRICAN_VIOLET, arcade.color.AIR_FORCE_BLUE]
)
def test_sensor_detects(color, fov, resolution):
    playground = Playground(size=(300, 300), background=arcade.color.ORANGE)

    agent = DynamicAgent()

    sensor = MockRaySensor(fov=fov, max_range=1000, resolution=resolution)
    agent.add(sensor)

    playground.add(agent, coord_center)

    ent_1 = DynamicElementFromGeometry(color=color, geometry="rectangle", size=(20, 20))
    playground.add(ent_1, ((40, 0), 0))

    assert playground.ray_compute is not None
    assert len(playground.ray_compute.sensors) == 1
    assert playground.ray_compute.sensors[0] == sensor

    playground.step(playground.null_action)

    assert sensor.updated

    # test sensor output
    assert sensor.observation.shape == (resolution, SIZE_OUTPUT_BUFFER)
    assert agent in sensor.invisible_entities

    # create a list with all angles from -fov/2 to fov/2,
    # and there are a number of values equal to resolutions
    hit_angles = [angle for angle in np.linspace(-fov / 2, fov / 2, resolution)]
    hit_angles = np.array(hit_angles)

    min_angle = -math.atan(10 / 30)
    max_angle = math.atan(10 / 30)

    # create mask of hit_angles that are between min_angle and max_angle
    mask = np.logical_and(hit_angles > min_angle, hit_angles < max_angle)

    assert np.all(sensor.observation[mask, 8] == ent_1.uid)
    assert np.all(sensor.observation[mask == False, 8] != ent_1.uid)

    assert np.all(sensor.observation[mask, 10:13] == color[:3])
    assert np.all(sensor.observation[mask == False, 10:13] != color[:3])

    assert np.all(sensor.observation[mask, 2] == 30)

    sensor.add_invisible_entity(ent_1)

    playground.step(playground.null_action)

    assert ent_1 in sensor.invisible_entities

    assert np.all(sensor.observation[mask, 8] == 0)
