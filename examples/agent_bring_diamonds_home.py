from simple_playgrounds.agent.part.interactives import Grasper
from simple_playgrounds.common.definitions import CollisionTypes
from simple_playgrounds.playground.collision_handlers import get_colliding_entities
from simple_playgrounds.playground.playground import Playground
from simple_playgrounds.playground.playgrounds.simple import WallClosedPG

from simple_playgrounds.element.diamond import Diamond
from simple_playgrounds.element.chest import Chest

from simple_playgrounds.agent.agents import HeadAgent
from simple_playgrounds.common.gui import GUI


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


chest = Chest(playground, ((200, 40), 0))
diamond = Diamond(playground, ((-200, 60), 0), chest)


chest_2 = Chest(playground, ((100, 40), 0))

agent = HeadAgent(playground)
Grasper(agent.base)

gui = GUI(playground, agent)
playground.run()
