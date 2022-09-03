import pytest
from spg.agent.controller import (
    ContinuousController,
    RangeController,
)

from spg.playground import Playground

# from spg.agent.sensor import RGB

from tests.mock_agents import MockAgent

# from tests.mock_entities import MockPhysicalMovable, MockPhysicalUnmovable


# def test_sensor_in_playground():

# playground = Playground()
# # agent = MockAgent()
# rgb = Rgb(agent.base)

#     playground.add(agent)

#     assert cam in agent._sensors
#     assert cam._pm_shapes[0] in agent._sensors

#     playground.remove(agent, definitive=False)

#     assert agent not in playground.agents
#     assert not playground.space.shapes
#     assert playground._shapes_to_entities != {}

#     playground.reset()

#     assert agent in playground.agents
#     assert cam._pm_shapes[0] in agent._sensors

#     playground.remove(agent, definitive=True)

#     assert agent not in playground.agents
#     assert not playground.space.shapes
#     assert playground._shapes_to_entities == {}

#     playground.reset()

#     assert agent not in playground.agents
