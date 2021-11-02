"""
Module containing classical RL environments.
"""
import random

from simple_playgrounds.playground.layouts import SingleRoom
from simple_playgrounds.playground.playground import PlaygroundRegister
from simple_playgrounds.common.position_utils import CoordinateSampler
from simple_playgrounds.element.elements.activable import VendingMachine
from simple_playgrounds.element.elements.gem import Coin
from simple_playgrounds.common import spawner


@PlaygroundRegister.register('basic_rl', 'coinmaster_singleroom')
class CoinMaster(SingleRoom):
    """
    The agent should collect the coins, grasp them,
    and bring them to the vending machine to collect rewards.
    """
    def __init__(self):

        super().__init__(size=(200, 200), wall_type='dark')

        self.agent_starting_area, self.area_prod, self.area_vending = self._assign_areas(
        )

        self.vending_machine = VendingMachine(allow_overlapping=False,
                                              reward=1)
        self.add_element(self.vending_machine, self.area_vending)

        self.spawner = spawner.Spawner(Coin,
                                       self.area_prod,
                                       max_elements_in_playground=5,
                                       production_limit=1000,
                                       entity_produced_params={
                               'graspable': True,
                               'vending_machine': self.vending_machine,
                               'reward': 1
                           })
        self.add_spawner(self.spawner)

        self.time_limit = 2000

    def _assign_areas(self):

        list_coord = [(50, 50), (50, 150), (150, 150), (150, 50)]
        random.shuffle(list_coord)

        # Starting area of the agent
        area_start_center = list_coord.pop()
        area_start = CoordinateSampler(center=area_start_center,
                                       area_shape='rectangle',
                                       size=(80, 80))

        agent_starting_area = area_start

        # invisible endzone at one corner of the game
        vm_center = list_coord.pop()
        prod_center = list_coord.pop()

        area_prod = CoordinateSampler(center=prod_center,
                                      area_shape='rectangle',
                                      size=(80, 80))
        area_vm = CoordinateSampler(center=vm_center,
                                    area_shape='rectangle',
                                    size=(80, 80))

        return agent_starting_area, area_prod, area_vm

    def reset(self):
        self.agent_starting_area, self.area_prod, self.area_vending = self._assign_areas(
        )

        for agent in self.agents:
            agent.initial_coordinates = self.agent_starting_area

        self.spawner.location_sampler = self.area_prod
        self.vending_machine.initial_position = self.area_vending

        super().reset()

    def _spawners_produce(self):

        super()._spawners_produce()
        self.vending_machine.accepted_coins = self.spawner.produced_entities
