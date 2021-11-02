import pytest
import time
import math

from simple_playgrounds.engine import Engine
from simple_playgrounds.agents.controllers import RandomContinuous
from simple_playgrounds.agents.agents import BaseAgent
import simple_playgrounds.agents.sensors as sensors
from simple_playgrounds.playgrounds.collection.profiling_playgrounds import BasicUnmovable


@pytest.fixture(scope="module", params=[sensors.RgbCamera,
                                        sensors.Lidar,
                                        sensors.SemanticRay,
                                        sensors.TopdownLocal,
                                        sensors.TopDownGlobal])
def type_sensor(request):
    return request.param


@pytest.fixture(scope="module", params=[50, 100, 200, 400, 600, 800, 1000, 5000])
def range_sensor(request):
    return request.param


@pytest.fixture(scope="module", params=[1, 8, 16, 24, 32, 64, 128, 256])
def res_sensor(request):
    return request.param


@pytest.fixture(scope="module", params=[True, False])
def invisible_anchor(request):
    return request.param


@pytest.fixture(scope="module", params=[ 200, 400, 800, 1000, 5000])
def pg_width(request):

    return request.param


n_steps = 10000
n_runs = 10

fname = 'profiling_unmovable.dat'


def test_basic_unmovable(pg_width, type_sensor, range_sensor, res_sensor, invisible_anchor):

    times = []

    for run in range(n_runs):

        my_agent = BaseAgent(controller=RandomContinuous(), lateral=True, interactive=False)

        if invisible_anchor:
            sensor = type_sensor(anchor = my_agent.base_platform,
                                 invisible_elements = [my_agent.base_platform],
                                 max_range =range_sensor,
                                 resolution=res_sensor,
                                 fov = math.pi)

        else:
            sensor = type_sensor(anchor=my_agent.base_platform,
                                 max_range=range_sensor,
                                 resolution=res_sensor,
                                 fov=math.pi)

        my_agent.add_sensor(sensor)

        n_elem_per_dim = int(pg_width / 50)
        size_elem = 20
        pg = BasicUnmovable(size=(pg_width, pg_width), size_elements=size_elem, n_elements_per_dim=n_elem_per_dim)

        pg.add_agent(my_agent)

        engine_ = Engine(playground=pg, screen=False, debug=False, time_limit=n_steps)

        t_start = time.time()
        while engine_.game_on:
            engine_.step(actions=my_agent.controller.generate_actions())
            engine_.update_observations()
        t_end = time.time()

        times.append(t_end-t_start)

    with open(fname, 'a') as f:

        for val in [pg_width, type_sensor, range_sensor, res_sensor, invisible_anchor]:
            f.write( str(val) + ';')

        f.write(str(n_steps/(sum(times)/n_runs))+'\n')


with open(fname, 'w') as f:
    for var_name in test_basic_unmovable.__code__.co_varnames:
        f.write(var_name + ';')

    f.write('time\n')