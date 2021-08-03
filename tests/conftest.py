import pytest

from simple_playgrounds.agents.agents import (BaseAgent, HeadAgent,
                                              HeadEyeAgent, FullAgent)
from simple_playgrounds.agents.parts.controllers import RandomDiscrete, RandomContinuous, External
from simple_playgrounds.playgrounds.collection import *

from simple_playgrounds.agents.sensors import (RgbCamera, GreyCamera, Lidar,
                                               Proximity, Touch, TopdownSensor,
                                               FullPlaygroundSensor,
                                               SemanticRay, SemanticCones)

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
                    TopdownSensor, FullPlaygroundSensor, SemanticRay,
                    SemanticCones
                ])
def any_sensor(request):
    return request.param


@pytest.fixture(scope="module", params=[RgbCamera, SemanticRay, SemanticCones])
def ray_sensor(request):
    return request.param


@pytest.fixture(scope="module", params=[2, 90, 180])
def fov(request):
    return request.param


@pytest.fixture(scope="module", params=[2, 100, 500])
def obs_range(request):
    return request.param


@pytest.fixture(scope="module", params=[2, 32, 64])
def resolution(request):
    return request.param


###########################
# Playgrounds
###########################

@pytest.fixture(scope="module",
                params=PlaygroundRegister.playgrounds['test'].items())
def pg_test_class(request):
    _, pg_class = request.param
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


###########################
# Elements
###########################

@pytest.fixture(scope="module", params=[True, False])
def movable(request):
    return request.param


@pytest.fixture(scope="module", params=[2, 10, 15])
def radius(request):
    return request.param


@pytest.fixture(scope="module", params=['square', 'rectangle', 'circle', 'pentagon', 'triangle', 'hexagon'])
def basic_element(request, movable, radius):

    if request.param == 'rectangle':
        return Physical(config_key=request.param, movable=movable, mass=10, size=(radius, radius))
    else:
        return Physical(config_key=request.param, movable=movable, mass=10, radius=radius)


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


