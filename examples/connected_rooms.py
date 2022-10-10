import math

from spg.agent import HeadAgent
from spg.element import Chest, Coin
from spg.element.wall import TiledLongColorWall
from spg.playground import ConnectedRooms, Playground, get_colliding_entities
from spg.utils.definitions import CollisionTypes
from spg.view import HeadAgentGUI


def coin_chest_collision(arbiter, _, data):

    playground: Playground = data["playground"]
    (coin, _), (chest, _) = get_colliding_entities(playground, arbiter)

    assert isinstance(coin, Coin)
    assert isinstance(chest, Chest)

    if coin.chest == chest:
        chest.activate(coin)

    return True


class ExampleRoom(ConnectedRooms):
    def __init__(self, n_pairs):

        n_rooms_min = 2 * n_pairs + 1

        n_w = int(math.sqrt(n_rooms_min)) + 1
        n_h = int(n_rooms_min / n_w) + 1

        super().__init__(
            room_layout=(n_w, n_h),
            size_room=(200, 200),
            doorstep_length=70,
            centered_doorstep=True,
            background=(23, 73, 71),
            wall_cls=TiledLongColorWall,
        )

        self._task_elems = []

        permutations = self._rng.permutation(len(self._room_centers))

        for pair_index in range(n_pairs):
            color = tuple(self._rng.integers(0, 255, 3))

            chest = Chest(color=color)
            self.add(
                chest,
                self._room_coordinate_sampler[permutations[pair_index * 2]],
                allow_overlapping=False,
            )
            self._task_elems.append(chest)

            coin = Coin(chest, color=color)
            coin.graspable = True
            self.add(
                coin,
                self._room_coordinate_sampler[permutations[pair_index * 2 + 1]],
                allow_overlapping=False,
            )
            self._task_elems.append(coin)

        self.agent = HeadAgent()
        self.add(self.agent, self._room_coordinate_sampler[-1], allow_overlapping=True)

        self.add_interaction(
            CollisionTypes.GEM, CollisionTypes.ACTIVABLE_BY_GEM, coin_chest_collision
        )

    def reset(self):

        permutations = self._rng.permutation(len(self._room_centers))
        for index_elem, elem in enumerate(self._task_elems):
            elem.initial_coordinates = self._room_coordinate_sampler[
                permutations[index_elem]
            ]

        for elem in self._task_elems:
            if isinstance(elem, Chest):
                elem.move_to(elem.initial_coordinates)

        self.agent.initial_coordinates = self._room_coordinate_sampler[permutations[-1]]

        return super().reset()

    def _has_terminated(self):

        count_coins = sum(1 for elem in self.elements if isinstance(elem, Coin))
        if not count_coins:
            self.agent.reward += 100
            return True
        return False


playground = ExampleRoom(3)
gui = HeadAgentGUI(playground, playground.agent, draw_sensors=True)
gui.run()
