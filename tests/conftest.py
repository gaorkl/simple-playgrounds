import pytest

from spg.components.agents.base import (
    ForwardContinuousAgent,
    ForwardDiscreteAgent,
    HolonomicContinuousAgent,
    HolonomicDiscreteAgent,
)
from spg.core.playground import EmptyPlayground
from tests.mock_agents import (
    DynamicAgentWithArm,
    DynamicAgentWithGrasper,
    DynamicAgentWithTrigger,
    StaticAgent,
    StaticAgentWithArm,
    StaticAgentWithTrigger,
)

###########################
# PLAYGROUND PROPERTIES
###########################


@pytest.fixture
def playground():
    pg = EmptyPlayground(size=(200, 200))
    yield pg
    # pg.reset()
    del pg


###########################
# ENTITY PROPERTIES
###########################


@pytest.fixture(scope="module", params=["segment", "circle", "square"])
def geometry(request):
    return request.param


@pytest.fixture(scope="module", params=["circle", "box", "decomposition", None])
def shape_approx(request):
    return request.param


@pytest.fixture(scope="module", params=[0, 50, 150])
def comm_radius(request):
    return request.param


@pytest.fixture(
    scope="function",
    params=[
        ForwardContinuousAgent,
        ForwardDiscreteAgent,
        HolonomicContinuousAgent,
        HolonomicDiscreteAgent,
        DynamicAgentWithArm,
        DynamicAgentWithGrasper,
        DynamicAgentWithTrigger,
    ],
)
def dynamic_agent_cls(request):
    return request.param


@pytest.fixture(
    scope="function", params=[StaticAgent, StaticAgentWithArm, StaticAgentWithTrigger]
)
def static_agent_cls(request):
    return request.param


# all agents
@pytest.fixture(
    scope="function",
    params=[
        ForwardContinuousAgent,
        ForwardDiscreteAgent,
        HolonomicContinuousAgent,
        HolonomicDiscreteAgent,
        DynamicAgentWithArm,
        DynamicAgentWithTrigger,
        DynamicAgentWithGrasper,
        StaticAgent,
        StaticAgentWithArm,
        StaticAgentWithTrigger,
    ],
)
def any_agents_cls(request):
    return request.param
