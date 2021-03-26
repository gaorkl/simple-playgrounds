import pytest

from simple_playgrounds.agents.agents import (BaseAgent, HeadAgent,
                                              HeadEyeAgent, TurretAgent)
from simple_playgrounds.agents.parts.controllers import Random
from simple_playgrounds.agents.parts.platform import (FixedPlatform,
                                                      ForwardBackwardPlatform,
                                                      ForwardPlatform,
                                                      ForwardPlatformDiscrete,
                                                      HolonomicPlatform)
from simple_playgrounds.playground import PlaygroundRegister

platform_classes = [
    ForwardPlatform, FixedPlatform, HolonomicPlatform, ForwardBackwardPlatform,
    ForwardPlatformDiscrete
]

agent_classes = [BaseAgent, HeadAgent, HeadEyeAgent, TurretAgent]


@pytest.fixture(scope="module", params=[True, False])
def is_interactive(request):
    return request.param


@pytest.fixture(scope="module", params=platform_classes)
def platform_cls(request):
    return request.param


@pytest.fixture(scope="module", params=agent_classes)
def agent_cls(request):
    return request.param


@pytest.fixture(scope="module",
                params=PlaygroundRegister.playgrounds['test'].items())
def pg_cls(request):
    pg_name, pg_class = request.param
    return pg_class


@pytest.fixture(scope="function")
def base_forward_agent():
    agent = BaseAgent(controller=Random(),
                      interactive=False,
                      platform=ForwardPlatform)
    return agent
