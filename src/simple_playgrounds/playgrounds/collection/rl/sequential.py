import itertools
import random

from ...playground import PlaygroundRegister
from ...layouts import GridRooms
from ....elements.collection.gem import Key, Coin
from ....elements.collection.activable import Lock, Dispenser, VendingMachine
from ....elements.collection.contact import Candy
from ....common.position_utils import CoordinateSampler


@PlaygroundRegister.register('basic_rl', 'dispenser_9rooms')
class DispenserEnv(GridRooms):
    """
        Environment composed of 3 rooms (3x1).
        The agent must reach the dispenser, activate it to produce candies in an other room,
        then collect the rewards.
    """
    def __init__(
        self,
        time_limit=1000,
        wall_texture_seed=None,
    ):

        super().__init__(size=(450, 300),
                         room_layout=(3, 2),
                         doorstep_size=60,
                         wall_type='colorful',
                         rng=wall_texture_seed,
                         )

        self.initial_agent_coordinates, self.area_prod, self.area_dispenser = self._assign_areas()

        self.dispenser = None
        self._place_scene_elements()

        self.time_limit = time_limit

    def _assign_areas(self):

        all_coords = set(itertools.product(range(self.grid_rooms.shape[0]),
                                           range(self.grid_rooms.shape[1]))
                         )

        coord_agent, coord_disp, coord_prod = random.sample(all_coords, 3)

        agent_starting_area = self.grid_rooms[coord_agent].get_area_sampler()

        area_dispenser = self.grid_rooms[coord_disp].get_area_sampler()
        area_prod = self.grid_rooms[coord_prod].get_area_sampler()

        return agent_starting_area, area_prod, area_dispenser

    def _place_scene_elements(self):

        self.dispenser = Dispenser(element_produced=Candy,
                                   production_area=self.area_prod,
                                   radius=10,
                                   temporary=True,
                                   allow_overlapping=False)
        self.add_element(self.dispenser, self.area_dispenser)

    def reset(self):
        self._remove_element_from_playground(self.dispenser)

        self.initial_agent_coordinates, self.area_prod, self.area_dispenser = self._assign_areas(
        )

        for agent in self.agents:
            agent.initial_coordinates = self.initial_agent_coordinates
        super().reset()

        self._place_scene_elements()


class DoorDispenserCoin(GridRooms):
    def __init__(
        self,
        time_limit=1000,
        wall_texture_seed=None,
    ):

        super().__init__(size=(450, 150),
                         room_layout=(3, 1),
                         doorstep_size=60,
                         wall_type='colorful',
                         wall_texture_seed=wall_texture_seed)

        self.time_limit = time_limit

        door = self.add_door(((1, 0), (2, 0)))

        area_key_center, area_key_shape = self.area_rooms[(0, 0)]
        area_key = CoordinateSampler(center=area_key_center,
                                     area_shape='rectangle',
                                     size=area_key_shape)
        key = Key(graspable=True)
        self.add_scene_element(key, area_key)
        lock = Lock(door=door, key=key)
        lock_position = self.random_position_on_wall((1, 0), 'right',
                                                     lock._radius)

        self.add_scene_element(lock, lock_position)

        vm_center, vm_shape = self.get_area((2, 0), 'up-right')
        area_vm = CoordinateSampler(center=vm_center,
                                    area_shape='rectangle',
                                    size=vm_shape)

        vm = VendingMachine()
        self.add_scene_element(vm, area_vm, allow_overlapping=False)

        dispenser_center, dispenser_shape = self.get_area((2, 0), 'down-right')
        area_dispenser = CoordinateSampler(center=dispenser_center,
                                           area_shape='rectangle',
                                           size=dispenser_shape)

        prod_center, prod_shape = self.area_rooms[(0, 0)]
        area_prod = CoordinateSampler(center=prod_center,
                                      area_shape='rectangle',
                                      size=prod_shape)

        dispenser = Dispenser(Coin,
                              production_area=area_prod,
                              entity_produced_params={
                                  'graspable': True,
                                  'vending_machine': vm
                              })
        self.add_scene_element(dispenser,
                               area_dispenser,
                               allow_overlapping=False)

        area_start_center, area_start_shape = self.area_rooms[(1, 0)]
        area_start = CoordinateSampler(center=area_start_center,
                                       area_shape='rectangle',
                                       size=area_start_shape)
        self.initial_agent_coordinates = area_start
