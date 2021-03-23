"""
Module containing classical RL environments.
"""
import random

from simple_playgrounds.playground import PlaygroundRegister
from simple_playgrounds.playgrounds.empty import SingleRoom, ConnectedRooms2D
from simple_playgrounds.playgrounds.scene_elements \
    import Basic, GoalZone, Candy, Dispenser, Coin, DeathZone, Field, VendingMachine
from simple_playgrounds.utils.position_utils import CoordinateSampler


@PlaygroundRegister.register('basic_rl', 'endgoal_cue')
class EndgoalRoomCue(SingleRoom):
    """
    Squared environment with obstacles.
    The agent must reach the correct corner, indicated by the color of
    a center object.
    """

    def __init__(self):

        super().__init__(size=(200, 200))

        # Starting area of the agent
        area_center, _ = self.area_rooms[(0, 0)]
        area_start = CoordinateSampler(center=area_center,
                                       area_shape='rectangle',
                                       width_length=(100, 100))
        self.agent_starting_area = area_start

        # Obstacles
        obstacle_1 = Basic(default_config_key='pentagon', radius=9)
        self.add_scene_element(obstacle_1, ((60, 30), 0.34))

        obstacle_2 = Basic(default_config_key='rectangle', width_length=[8, 12])
        self.add_scene_element(obstacle_2, ((130, 150), 1.7))

        obstacle_3 = Basic(default_config_key='square', radius=8)
        self.add_scene_element(obstacle_3, ((40, 140), 0.4))

        obstacle_4 = Basic(physical_shape='triangle', radius=14, texture=(150, 200, 200))
        self.add_scene_element(obstacle_4, ((160, 60), 0))

        self.goal = None
        self.cue = None

        self.goal_locations = (((20, 20), 0), ((180, 20), 0), ((180, 180), 0), ((20, 180), 0))
        self.cue_colors = ((200, 50, 200), (50, 200, 50), (200, 50, 50), (50, 50, 200))

        self._set_goal()
        self.time_limit = 2000
        self.time_limit_reached_reward = -1

    def _set_goal(self):

        index_goal = random.randint(0, 3)
        loc = self.goal_locations[index_goal]
        col = self.cue_colors[index_goal]

        if self.goal is not None:
            self.remove_scene_element(self.goal)
            self.remove_scene_element(self.cue)

        self.cue = Basic(physical_shape='circle', radius=10, texture=col, is_temporary_entity=True)
        self.add_scene_element(self.cue, ((100, 100), 0))

        self.goal = GoalZone(reward=1, is_temporary_entity=True)
        self.add_scene_element(self.goal, loc)

        for i in range(4):
            if i != index_goal:
                loc = self.goal_locations[i]
                other_goal = DeathZone(reward=-1, is_temporary_entity=True)
                self.add_scene_element(other_goal, loc)

    def reset(self):
        super().reset()
        self._set_goal()


@PlaygroundRegister.register('basic_rl', 'endgoal_9rooms')
class Endgoal9Rooms(ConnectedRooms2D):
    """
    Squared environment composed of 9 rooms (3x3).
    The agent must reach the invisible goal in the left-down corner.
    Each wall has a different color.
    """
    def __init__(self):

        super().__init__(size=(600, 600), room_layout=(3, 3), wall_type='colorful')

        # Starting area of the agent
        area_start = CoordinateSampler(center=(300, 300),
                                       area_shape='rectangle', width_length=(600, 600))
        self.agent_starting_area = area_start

        # invisible endzone at one corner of the game
        invisible_endzone = GoalZone(reward=10)
        self.add_scene_element(invisible_endzone, ((20, 20), 0))

        self.time_limit = 3000


@PlaygroundRegister.register('basic_rl', 'dispenser_6rooms')
class DispenserEnv(ConnectedRooms2D):
    """
        Environment composed of 3 rooms (3x1).
        The agent must reach the dispenser, activate it to produce candies in an other room,
        then collect the rewards.
    """

    def __init__(self):

        super().__init__(size=(300, 200), room_layout=(3, 2))

        self.agent_starting_area, self.area_prod, self.area_dispenser = self._assign_areas()

        self.dispenser = None
        self._place_scene_elements()

        self.time_limit = 2000

    def _assign_areas(self):
        list_room_coordinates = [room_coord for room_coord, _ in self.area_rooms.items()]
        random.shuffle(list_room_coordinates)

        # Starting area of the agent
        area_start_center, area_start_shape = self.area_rooms[list_room_coordinates.pop()]
        area_start = CoordinateSampler(center=area_start_center,
                                       area_shape='rectangle', width_length=area_start_shape)
        agent_starting_area = area_start

        # invisible endzone at one corner of the game
        dispenser_center, dispenser_shape = self.area_rooms[list_room_coordinates.pop()]
        prod_center, prod_shape = self.area_rooms[list_room_coordinates.pop()]

        area_prod = CoordinateSampler(center=prod_center,
                                      area_shape='rectangle', width_length=prod_shape)
        area_dispenser = CoordinateSampler(center=dispenser_center,
                                           area_shape='rectangle', width_length=dispenser_shape)

        return agent_starting_area, area_prod, area_dispenser

    def _place_scene_elements(self):

        self.dispenser = Dispenser(Candy, production_area=self.area_prod,
                                   radius=10, is_temporary_entity=True, allow_overlapping=False)
        self.add_scene_element(self.dispenser, self.area_dispenser)

    def reset(self):
        self.remove_scene_element(self.dispenser)

        self.agent_starting_area, self.area_prod, self.area_dispenser = self._assign_areas()

        for agent in self.agents:
            agent.initial_coordinates = self.agent_starting_area
        super().reset()

        self._place_scene_elements()


@PlaygroundRegister.register('basic_rl', 'coinmaster_singleroom')
class CoinMaster(SingleRoom):
    """
    The agent should collect the coins, grasp them,
    and bring them to the vending machine to collect rewards.
    """
    def __init__(self):

        super().__init__(size=(200, 200), wall_type='dark')

        self.agent_starting_area, self.area_prod, self.area_vending = self._assign_areas()

        self.field = Field(Coin, self.area_prod, limit=5, total_limit=1000,
                           entity_produced_params={'graspable': True, 'reward': 1})
        self.add_scene_element(self.field)

        self.vending_machine = VendingMachine(allow_overlapping=False, reward=1)
        self.add_scene_element(self.vending_machine, self.area_vending)

        self.time_limit = 2000

    def _assign_areas(self):

        list_coord = [(50, 50), (50, 150), (150, 150), (150, 50)]
        random.shuffle(list_coord)

        # Starting area of the agent
        area_start_center = list_coord.pop()
        area_start = CoordinateSampler(center=area_start_center, area_shape='rectangle',
                                       width_length=[80, 80])

        agent_starting_area = area_start

        # invisible endzone at one corner of the game
        vm_center = list_coord.pop()
        prod_center = list_coord.pop()

        area_prod = CoordinateSampler(center=prod_center,
                                      area_shape='rectangle', width_length=[80, 80])
        area_vm = CoordinateSampler(center=vm_center, area_shape='rectangle',
                                    width_length=[80, 80])

        return agent_starting_area, area_prod, area_vm

    def reset(self):
        self.agent_starting_area, self.area_prod, self.area_vending = self._assign_areas()

        for agent in self.agents:
            agent.initial_coordinates = self.agent_starting_area

        self.field.location_sampler = self.area_prod
        self.vending_machine.initial_position = self.area_vending

        super().reset()

    def _fields_produce(self):

        super()._fields_produce()
        self.vending_machine.accepted_coins = self.field.produced_entities
