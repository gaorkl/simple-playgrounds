from spg.utils.definitions import CollisionTypes
from spg.playground.collision_handlers import get_colliding_entities
from spg.playground import Playground
from spg.playground import WallClosedPG

from spg.element import Diamond, Chest

from spg.agent import HeadAgent
from spg.view import GUI


def diamond_chest_collision(arbiter, space, data):

    playground: Playground = data["playground"]
    (diamond, _), (chest, _) = get_colliding_entities(playground, arbiter)

    assert isinstance(diamond, Diamond)
    assert isinstance(chest, Chest)

    if diamond.chest == chest:
        chest.activate(diamond)

    return True


playground = WallClosedPG(size=(500, 200))
playground.add_interaction(
    CollisionTypes.GEM, CollisionTypes.ACTIVABLE_BY_GEM, diamond_chest_collision
)


chest = Chest()
playground.add(chest, ((200, 40), 0))
diamond = Diamond(chest)
diamond.graspable = True
playground.add(diamond, ((-200, 60), 0))


chest_2 = Chest()
playground.add(chest_2, ((100, 40), 0))

agent = HeadAgent()

playground.add(agent)

gui = GUI(playground, agent)
gui.run()
