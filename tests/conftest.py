import pytest

from simple_playgrounds.agents.agents import (BaseAgent, HeadAgent,
                                              HeadEyeAgent, FullAgent)
from simple_playgrounds.agents.parts.controllers import RandomDiscrete, RandomContinuous, External
from simple_playgrounds.playgrounds.collection.demo_playgrounds import Basics, Zones, Teleports, ExtraTeleports
from simple_playgrounds.playgrounds.playground import PlaygroundRegister
from simple_playgrounds.playgrounds.layouts import SingleRoom

from simple_playgrounds.agents.sensors import (RgbCamera, GreyCamera, Lidar,
                                               Proximity, Touch, TopdownLocal,
                                               TopDownGlobal, PerfectSemantic,
                                               SemanticRay, SemanticCones, Position, Velocity)

from simple_playgrounds.elements.collection.basic import Physical


###########################
# AGENT BODY
###########################


@pytest.fixture(scope="module", params=[True, False])
def is_interactive(request):
    return request.param


@pytest.fixture(scope="module", params=[True, False])
def going_backward(request):
    return request.param


@pytest.fixture(scope="module", params=[True, False])
def moving_laterally(request):
    return request.param


@pytest.fixture(scope="module", params=[RandomDiscrete, RandomContinuous])
def random_controller(request):
    return request.param


@pytest.fixture(scope="module", params=[BaseAgent, HeadAgent, HeadEyeAgent, FullAgent])
def all_agent_cls(request):
    return request.param


@pytest.fixture(scope="function")
def base_forward_agent_random():
    agent = BaseAgent(
        controller=RandomDiscrete(),
        interactive=False,
    )
    return agent


@pytest.fixture(scope="function")
def base_forward_interactive_agent_external():
    agent = BaseAgent(
        controller=External(),
        interactive=True,
    )
    return agent


###########################
# AGENT BODY
###########################


@pytest.fixture(scope="module",
                params=[
                    RgbCamera, GreyCamera, Lidar, Touch, Proximity,
                    TopdownLocal, TopDownGlobal, SemanticRay,
                    SemanticCones, PerfectSemantic, Position, Velocity
                ])
def any_sensor(request):
    return request.param


@pytest.fixture(scope="module", params=[RgbCamera, SemanticRay, SemanticCones, PerfectSemantic])
def ray_sensor(request):
    return request.param


@pytest.fixture(scope="module", params=[1, 180])
def fov(request):
    return request.param


@pytest.fixture(scope="module", params=[100, 500])
def obs_range(request):
    return request.param


@pytest.fixture(scope="module", params=[1, 32])
def resolution(request):
    return request.param


###########################
# Playgrounds
###########################

@pytest.fixture(scope="module",
                params=PlaygroundRegister.playgrounds['demo'].items())
def pg_test_class(request):
    _, pg_class = request.param
    return pg_class


@pytest.fixture(scope="module",
                params=[Basics, Zones, Teleports, ExtraTeleports])
def pg_sensor_class(request):
    pg_class = request.param
    return pg_class


@pytest.fixture(scope="module",
                params=PlaygroundRegister.playgrounds['basic_rl'].items())
def pg_rl_class(request):
    _, pg_class = request.param
    return pg_class


@pytest.fixture(scope="function")
def empty_playground():
    pg = SingleRoom(
        size=(100, 100)
    )
    return pg


@pytest.fixture(scope="module", params=['colorful', 'classic', 'light', 'dark'])
def wall_type(request):
    return request.param


###########################
# Elements
###########################

@pytest.fixture(scope="module", params=[True, False])
def is_movable(request):
    return request.param


@pytest.fixture(scope="module", params=[2, 10, 15])
def elem_radius(request):
    return request.param


@pytest.fixture(
    scope='module',
    params=[
        'square',
        'rectangle',
        'circle',
        'pentagon',
        'triangle',
        'hexagon',
        'polygon',
    ],
)
def basic_element(request, is_movable, elem_radius):

    if request.param == 'rectangle':
        kwargs = {'size': (elem_radius, elem_radius)}
    elif request.param == 'polygon':
        kwargs = {'vertices': [[-10, 0], [0, 5], [-2, 0], [0, -5], [-10, 0]]}
    else:
        kwargs = {'radius': elem_radius}

    return Physical(
        config_key=request.param, movable=is_movable, mass=10, **kwargs)


####################
# Others
####################

@pytest.fixture(scope="module", params=[5, [5, 10], (5, 10)])
def periods(request):
    return request.param


@pytest.fixture(scope="module", params=[-5, 0, 5])
def reward(request):
    return request.param


@pytest.fixture(scope="module", params=[0, 1, 10])
def pos_reward(request):
    return request.param


@pytest.fixture(scope="module", params=[ (0, 10), (10, 0), (5, 10), (10, 10), (10, 5) ])
def field_limits(request):
    return request.param

####################
# Communication
####################


@pytest.fixture(scope="module", params=[-1, 0, 50, 150] )
def comm_radius(request):
    return request.param

