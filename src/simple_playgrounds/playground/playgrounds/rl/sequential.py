import itertools
import random

from simple_playgrounds.playground.layouts import GridRooms, LineRooms
from simple_playgrounds.playground.playground import PlaygroundRegister
from simple_playgrounds.common.position_utils import CoordinateSampler
from simple_playgrounds.element.elements.activable import Lock, Dispenser, VendingMachine
from simple_playgrounds.element.elements.contact import Candy
from simple_playgrounds.element.elements.gem import Key, Coin


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

        super().__init__(
            size=(450, 300),
            room_layout=(3, 2),
            doorstep_size=60,
            wall_type='colorful',
            playground_seed=wall_texture_seed,
        )

        self.initial_agent_coordinates, self.area_prod, self.area_dispenser = self._assign_areas(
        )

        self.dispenser = None
        self._place_scene_elements()

        self.time_limit = time_limit

    def _assign_areas(self):

        all_coords = list(
            itertools.product(range(self.grid_rooms.shape[0]),
                              range(self.grid_rooms.shape[1])))

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


@PlaygroundRegister.register('basic_rl', 'door_dispenser_coin')
class DoorDispenserCoin(LineRooms):
    def __init__(
        self,
        time_limit=1000,
        wall_texture_seed=None,
    ):

        super().__init__(size=(450, 150),
                         number_rooms=3,
                         doorstep_size=60,
                         wall_type='colorful',
                         playground_seed=wall_texture_seed)

        self.time_limit = time_limit

        doorstep_1 = self.grid_rooms[0, 1].doorstep_right
        door = doorstep_1.generate_door()
        self.add_element(door)

        lock = Lock(door=door)
        lock_position = self.grid_rooms[0, 1].get_random_position_on_wall('right', element=lock)
        self.add_element(lock, lock_position)

        area_key = self.grid_rooms[0, 0].get_area_sampler()
        key = Key(graspable=True, locked_elem=lock)
        self.add_element(key, area_key, allow_overlapping=False)

        vm_center, vm_shape = self.grid_rooms[0, 2].get_partial_area('up-right')
        area_vm = CoordinateSampler(center=vm_center,
                                    area_shape='rectangle',
                                    size=vm_shape)

        vm = VendingMachine(reward=5)
        self.add_element(vm, area_vm, allow_overlapping=False)

        dispenser_center, dispenser_shape = self.grid_rooms[0, 2].get_partial_area('down-right')
        area_dispenser = CoordinateSampler(center=dispenser_center,
                                           area_shape='rectangle',
                                           size=dispenser_shape)

        area_prod = self.grid_rooms[0, 0].get_area_sampler()

        dispenser = Dispenser(Coin,
                              production_area=area_prod,
                              entity_produced_params={
                                  'graspable': True,
                                  'vending_machine': vm
                              })
        self.add_element(dispenser,
                         area_dispenser,
                         allow_overlapping=False)

        self.initial_agent_coordinates = self.grid_rooms[0, 1].get_area_sampler()

