from simple_playgrounds.playground.playground import EmptyPlayground

from simple_playgrounds.agent.agent import Agent
from simple_playgrounds.agent.parts import MobilePlatform
from simple_playgrounds.agent.actuator.actuators import ForceActuator

class MockAgent(Agent):

    def __init__(self):




def test_traversable_traversable(custom_contour, custom_contour_2):

    playground = EmptyPlayground()

    # Two traversable shouldn't collide with either traversables or non-traversables

    ent_1 = MockPhysical(contour=custom_contour, traversable=True, movable=True, mass=5)
    playground.add(ent_1, ((0, 0), 0))

    ent_2 = MockPhysical(contour=custom_contour_2, traversable=True, movable=True, mass=5)
    playground.add(ent_2, ((0, 1), 0))

    playground.step()

    assert ent_1.coordinates == ((0, 0), 0)
    assert ent_2.coordinates == ((0, 1), 0)

