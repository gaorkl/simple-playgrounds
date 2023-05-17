import math

import matplotlib.pyplot as plt
import numpy as np

from spg.playground import EmptyPlayground
from spg.playground.actions import fill_action_space
from spg.view import View
from tests.mock_agents import DynamicAgent, DynamicAgentWithArm
from tests.mock_entities import DynamicElementFromGeometry

coord_center = (0, 0), 0
coord_shifted_center = (100, 0), 0


def test_move_object():

    playground = EmptyPlayground(size=(400, 400))

    ent_1 = DynamicElementFromGeometry(
        geometry="circle", radius=10, color=(100, 200, 13)
    )
    playground.add(ent_1, coord_shifted_center)

    agent = DynamicAgent(name="agent")
    playground.add(agent, coord_center)

    view = View(playground, size_on_playground=(400, 400), center=(0, 0), scale=1)
    img = view.get_np_img()

    action = {agent.name: {agent.name: (1, 0, 0)}}
    action = fill_action_space(playground, action)

    for i in range(20):
        playground.step(action)

    img_2 = view.get_np_img()
    plt.imshow(img_2)
    plt.show()

    assert not np.all(img == img_2)


def test_delete_agent():

    playground = EmptyPlayground(size=(400, 400))

    agent = DynamicAgentWithArm(
        rotation_range=math.pi / 2, arm_angle=0, arm_position=(10, 10), name="agent"
    )
    playground.add(agent, coord_center)

    view = View(playground, size_on_playground=(400, 400), center=(0, 0), scale=1)

    img = view.get_np_img()

    playground.remove(agent)

    view.update(force=True)
    img_2 = view.get_np_img()

    assert not np.all(img == img_2)
    assert np.sum(img_2) == 0
