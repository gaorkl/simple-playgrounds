from simple_playgrounds.playgrounds.empty import SingleRoom, ConnectedRooms2D, LinearRooms
from simple_playgrounds.entities.texture import UniqueRandomTilesTexture
from simple_playgrounds.entities.scene_elements import *
from simple_playgrounds.utils import PositionAreaSampler, Trajectory
from simple_playgrounds.playgrounds.playground import PlaygroundRegister


@PlaygroundRegister.register('rl_endgoal_singleroom')
class EndgoalRoom(SingleRoom):

    def __init__(self):

        wall_texture = UniqueRandomTilesTexture(n_colors=4, delta_uniform=15, color_min=(50, 50, 50),
                                                color_max=(150, 150, 150), radius=100)

        super().__init__(size = (200, 200), wall_texture = wall_texture)

        # Starting area of the agent
        area_center, _ = self.area_rooms[(0,0)]
        area_start = PositionAreaSampler(center=area_center, area_shape='rectangle', width_length=(100,100))

        self.agent_starting_area = area_start

        # invisible endzone at one corner of the game
        invisible_endzone = GoalZone((20,20,0), reward = 10)
        self.add_scene_element(invisible_endzone)

        self.time_limit = 1000

@PlaygroundRegister.register('rl_endgoal_9rooms')
class Endgoal9Rooms(ConnectedRooms2D):

    def __init__(self):

        super().__init__(size = (600, 600), n_rooms=(3,3), wall_type='colorful')

        # Starting area of the agent
        area_start = PositionAreaSampler(center=(300, 300), area_shape='rectangle', width_length=(600, 600))
        self.agent_starting_area = area_start

        # invisible endzone at one corner of the game
        invisible_endzone = GoalZone((20, 20, 0), reward = 10)
        self.add_scene_element(invisible_endzone)

        self.time_limit = 10000

@PlaygroundRegister.register('rl_dispenser_2rooms')
class DispenserEnv(LinearRooms):

    def __init__(self):

        super().__init__(size = (200, 100), n_rooms=2, wall_type='colorful')

        # Starting area of the agent
        area_start = PositionAreaSampler(center=(50, 50), area_shape='rectangle', width_length=(100, 100))
        self.agent_starting_area = area_start

        # invisible endzone at one corner of the game

        area_prod = PositionAreaSampler(center=(50, 50), area_shape='rectangle', width_length=(50, 50))
        dispenser = Dispenser((150, 50, 0), production_area = area_prod, entity_produced=Candy, radius = 10)
        self.add_scene_element(dispenser)

        self.time_limit = 2000
