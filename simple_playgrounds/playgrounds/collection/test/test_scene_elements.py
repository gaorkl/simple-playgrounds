from simple_playgrounds.playgrounds.empty import SingleRoom
from simple_playgrounds.entities import Field
from simple_playgrounds.entities.scene_elements import *
from simple_playgrounds.utils import PositionAreaSampler, Trajectory
from simple_playgrounds.playgrounds.playground import PlaygroundRegister

import math


@PlaygroundRegister.register('test_basic')
class Basics(SingleRoom):

    def __init__(self, size = (200, 200), **playground_params):

        super().__init__(size = size, **playground_params)

        rectangle_01 = Basic([150, 160, 0.2], default_config_key='rectangle')
        self.add_scene_element(rectangle_01)

        circle_01 = Basic([50, 50, 0], default_config_key='circle',
                                           movable=False, mass=100, texture=[150, 150, 150])
        self.add_scene_element(circle_01)

        square_01 = Basic([150, 60, math.pi/4], default_config_key='square', movable=True, mass=10)
        self.add_scene_element(square_01)

        pentagon_01 = Basic([50, 160, 0], default_config_key='pentagon', radius = 15)
        self.add_scene_element(pentagon_01)

        hexagon_01 = Basic([100, 100, 0], default_config_key='hexagon', mass = 5)
        self.add_scene_element(hexagon_01)

        self.agent_starting_area = [100, 60, 0]

@PlaygroundRegister.register('test_grasp')
class Graspables(SingleRoom):

    def __init__(self, size = (200, 200), **playground_params):

        super().__init__(size = size, **playground_params)

        rectangle_01 = Basic([150, 160, 0.2], default_config_key='rectangle', graspable = True, mass = 10)
        self.add_scene_element(rectangle_01)

        circle_01 = Basic([50, 50, 0], default_config_key='circle',
                                           graspable=True, mass=10, texture=[150, 150, 150])
        self.add_scene_element(circle_01)

        square_01 = Basic([150, 60, math.pi/4], default_config_key='square', graspable=True, mass=10)
        self.add_scene_element(square_01)

        pentagon_01 = Basic([50, 160, 0], default_config_key='pentagon', radius = 15, graspable = True, mass = 10)
        self.add_scene_element(pentagon_01)

        hexagon_01 = Basic([100, 100, 0], default_config_key='hexagon', graspable = True, mass = 10)
        self.add_scene_element(hexagon_01)

        self.agent_starting_area = [100, 60, 0]


@PlaygroundRegister.register('test_contacts')
class Contacts(SingleRoom):

    def __init__(self, size = (200, 200), **playground_params):

        super().__init__(size = size, **playground_params)

        endgoal_01 = VisibleEndGoal([20, 180, 0], reward=50)
        self.add_scene_element(endgoal_01)

        deathtrap_01 = VisibleDeathTrap([180, 180, 0])
        self.add_scene_element(deathtrap_01)

        poison = Poison( initial_position = [15, 15, 0])
        self.add_scene_element(poison)

        poison_area = PositionAreaSampler(area_shape='rectangle', center=[100, 150], width_length=[20, 20])
        for i in range(5):
            poison = Poison(poison_area)
            self.add_scene_element(poison)

        candy_area = PositionAreaSampler(area_shape='rectangle', center=[50, 100], width_length=[20, 20])
        for i in range(5):
            candy = Candy(candy_area)
            self.add_scene_element(candy)

        # outside on purpose
        outside_area = PositionAreaSampler(area_shape='rectangle', center=[200, 100], width_length=[50, 50])
        for i in range(8):
            candy = Candy(outside_area)
            self.add_scene_element(candy)

        self.agent_starting_area = [100, 60, 0]


@PlaygroundRegister.register('test_zones')
class Zones(SingleRoom):

    def __init__(self, size = (200, 200), **playground_params):

        super().__init__(size = size, **playground_params)

        goal_1 = GoalZone([20, 20, 0])
        self.add_scene_element(goal_1)

        goal_2 = GoalZone([180, 20, 0])
        self.add_scene_element(goal_2)

        death_1 = DeathZone([20, 180, 0], reward=-25)
        self.add_scene_element(death_1)

        death_2 = DeathZone([180, 180, 0])
        self.add_scene_element(death_2)

        healing_1 = HealingZone([50, 100, 0])
        self.add_scene_element(healing_1)

        toxic_1 = ToxicZone([150, 100, 0])
        self.add_scene_element(toxic_1)

        self.agent_starting_area = [100, 60, 0]

@PlaygroundRegister.register('test_interactives')
class Interactives(SingleRoom):

    def __init__(self, size = (300, 300), **playground_params):

        super().__init__(size = size, **playground_params)

        goal_1 = GoalZone([20, 20, 0])
        self.add_scene_element(goal_1)

        apple = Apple([100, 50, 0], physical_shape = 'pentagon', graspable = True)
        self.add_scene_element(apple)

        rotten = RottenApple([100, 100, 0])
        self.add_scene_element(rotten)

        area_1 = PositionAreaSampler(area_shape='rectangle', center=[200, 150], width_length=[20, 50])
        dispenser_1 = Dispenser(
            [150, 150, 0],
            entity_produced=Poison,
            production_area=area_1
        )
        self.add_scene_element(dispenser_1)

        area_2 = PositionAreaSampler(area_shape='gaussian', center=[150, 50], variance = 300, radius=60)
        dispenser_2 = Dispenser(
            [100, 150, 0],
            entity_produced=Candy,
            production_area=area_2
        )
        self.add_scene_element(dispenser_2)

        dispenser_3 = Dispenser(
            [200, 150, 0],
            entity_produced=Candy,
            entity_produced_params={'radius':3, 'reward':42},
            movable=True,
            mass=5
        )
        self.add_scene_element(dispenser_3)

        key_chest = Key([50, 200, 0], default_config_key='pentagon', radius = 7, graspable = True, mass = 10)
        self.add_scene_element(key_chest)

        treasure = Apple([0, 0, 0])
        chest = Chest([100, 200,0.2], key = key_chest, treasure = treasure, width_length = [20, 50])
        self.add_scene_element(chest)

        vending = VendingMachine([200, 200, 0])
        self.add_scene_element(vending)

        coin = Coin([150, 200, 0], graspable=True)
        self.add_scene_element(coin)
        vending.accepted_coins.append(coin)

        coin = Coin([150, 220, 0], graspable=True)
        self.add_scene_element(coin)
        vending.accepted_coins.append(coin)

        coin = Coin([150, 240, 0], graspable=True)
        self.add_scene_element(coin)
        vending.accepted_coins.append(coin)

        self.agent_starting_area = [130, 60, 0]


@PlaygroundRegister.register('test_conditioning')
class Conditioning(SingleRoom):

    def __init__(self, size = (300, 300), **playground_params):

        super(Conditioning, self).__init__(size = size, **playground_params)

        lever = Lever([100, 50, 0])
        self.add_scene_element(lever)

        light_01 = ConditionedColorChanging([150, 100, 0], conditioned_entity=lever, timers=[100, 100],
                                            textures=[[100, 200, 0], [200, 100, 200]])
        self.add_scene_element(light_01)

        self.agent_starting_area = [100, 60, 0]


@PlaygroundRegister.register('test_doors')
class Doors(SingleRoom):

    def __init__(self, size = (300, 300), **playground_params):

        super().__init__(size = size, **playground_params)

        door_1 = Door( [100, 150, math.pi/2])
        self.add_scene_element(door_1)
        switch_1 = OpenCloseSwitch( [100, 50, 0], door = door_1 )
        self.add_scene_element(switch_1)

        door_2 = Door( [150, 150, math.pi/2])
        self.add_scene_element(door_2)

        timerswitch = TimerSwitch(initial_position=[150, 90, 0], door=door_2, time_open = 20)
        self.add_scene_element(timerswitch)

        door_3 = Door([200, 150, math.pi / 2])
        self.add_scene_element(door_3)

        pushbutton = PushButton( [200, 90, 0], door=door_3)
        self.add_scene_element(pushbutton)

        door_4 = Door([250, 150, math.pi / 2])
        key = Key( [250, 60, math.pi/2], graspable = True, interaction_range = 5, mass = 30)
        lock = Lock( [250, 90, 0], door = door_4, key = key,  )

        self.add_scene_element(door_4)
        self.add_scene_element(key)
        self.add_scene_element(lock)

        self.agent_starting_area = [40, 40, 0]


@PlaygroundRegister.register('test_proximity')
class Proximity(SingleRoom):

    def __init__(self, size = (200, 200), **playground_params):

        super().__init__(size = size, **playground_params)

        fairy = Fairy([80, 150, 0])
        self.add_scene_element(fairy)

        fireball = Fireball([150, 80, 0])
        self.add_scene_element(fireball)

        goal_1 = GoalZone([20, 20, 0])
        self.add_scene_element(goal_1)

        self.agent_starting_area = [100, 60, 0]


@PlaygroundRegister.register('test_fields')
class Fields(SingleRoom):

    def __init__(self, size = (200, 200), **playground_params):

        super(Fields, self).__init__(size = size, **playground_params)

        area_1 = PositionAreaSampler(area_shape='rectangle', center=[70, 70], width_length=[30, 100])
        field = Field(Poison, production_area=area_1)
        self.add_scene_element(field)

        area_2 = PositionAreaSampler(area_shape='rectangle', center=[200, 70], width_length=[50, 50])
        field = Field(Candy, production_area=area_2)
        self.add_scene_element(field)

        self.agent_starting_area = [100, 60, 0]


@PlaygroundRegister.register('test_trajectories')
class Trajectories(SingleRoom):

    def __init__(self, size = (200, 200), **playground_params):

        super().__init__(size = size, **playground_params)

        trajectory = Trajectory('waypoints', 300, waypoints=[[20, 20], [20, 180], [180,180], [180,20]])
        goal_1 = GoalZone(trajectory)
        self.add_scene_element(goal_1)

        trajectory = Trajectory('shape', 200, 8, shape='square', center=[100, 70, 0], radius=50)
        fireball = Fireball(trajectory)
        self.add_scene_element(fireball)

        trajectory = Trajectory('shape', 100, 8, shape='pentagon', center = [50, 150, 0], radius= 30, counter_clockwise = True)
        fireball = Fireball(trajectory)
        self.add_scene_element(fireball)

        self.agent_starting_area = [100, 60, 0]
