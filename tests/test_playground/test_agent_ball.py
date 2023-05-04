from spg import Ball
from spg import HeadAgent
from spg import Room
from spg.playground.actions import fill_action_space


def test_scenario():

    playground = Room(size=(1000, 200))
    ball = Ball()
    playground.add(ball, ((200, 0), 0))

    agent = HeadAgent(name="agent")
    playground.add(agent)

    agent_forward_action = {agent.name: {"base": {"motor": {"forward_force": 1}}}}
    action = fill_action_space(playground, agent_forward_action)

    for _ in range(200):
        playground.step(action)

    assert ball.position != (200, 0)
    assert agent.position != (0, 0)
