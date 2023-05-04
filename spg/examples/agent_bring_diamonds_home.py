import arcade

from spg import Chest, Diamond
from spg import HeadAgent
from spg import Playground, Room
from spg import get_colliding_entities
from spg.definitions import CollisionTypes
from spg.view import HeadAgentGUI


def diamond_chest_collision(arbiter, _, data):

    playground: Playground = data["playground"]
    (diamond, _), (chest, _) = get_colliding_entities(playground, arbiter)

    assert isinstance(diamond, Diamond)
    assert isinstance(chest, Chest)

    if diamond.chest == chest:
        chest.activate(diamond)

    return True


playground = Room(size=(500, 200), wall_color=arcade.color.AMARANTH_PURPLE)
playground.add_interaction(
    CollisionTypes.GEM, CollisionTypes.ACTIVABLE_BY_GEM, diamond_chest_collision
)


chest = Chest(color=arcade.color.GUPPIE_GREEN)
playground.add(chest, ((200, 40), 0))
diamond = Diamond(chest)
diamond.graspable = True
playground.add(diamond, ((-200, 60), 0))


chest_2 = Chest(color=arcade.color.YELLOW_GREEN)
playground.add(chest_2, ((100, 40), 0))

agent = HeadAgent()

playground.add(agent)

gui = HeadAgentGUI(playground, agent)
gui.run()
