from simple_playgrounds.agent.agents import BaseAgent
from simple_playgrounds.agent.controllers import External
from simple_playgrounds.playground.playground import EmptyPlayground
from simple_playgrounds.entity.contour import Contour

from tests.mock_entities import MockPhysical

def test_moving_element():
    playground = EmptyPlayground()
    
    agent = BaseAgent(
        controller=External(),
        interactive=False,
        rotate=False,
        lateral=False
    )
    actions = {agent: {agent.longitudinal_force: 1.}}

    playground.add(agent, ((50, 100), 0))
    
    
    contour = Contour(shape='circle', radius=size_on_pg[0]*2)
    ent_1 = MockPhysical(contour=contour, movable=True, mass=5)
    playground.add(ent_1, ((0, 0), 0))



    playground.add_element(basic_element, ((100, 100), 0))

    engine = Engine(playground, time_limit=100)

    while engine.game_on:
        engine.step(actions)

    if basic_element._movable:
        assert agent.position[0] > 100
        assert basic_element.position[0] > 100
    else:
        assert basic_element.position[0] == 100
