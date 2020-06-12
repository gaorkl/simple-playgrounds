from flatland.playgrounds.empty import SingleRoom
from flatland.utils.position_utils import Trajectory
from flatland.entities import *
import math


class Basic_01(SingleRoom):

    def __init__(self, size = (200, 200), **playground_params):

        super(Basic_01, self).__init__(size = size, **playground_params)

        rectangle_01 = Basic([150, 160, 0.2], default_config_key='rectangle')
        self.add_entity(rectangle_01)

        circle_01 = EntityGenerator.create('basic', initial_position=[50, 60, 0], default_config_key='circle',
                                           movable=True, mass=100, texture=[150, 150, 150])
        self.add_entity(circle_01)

        square_01 = Basic([150, 60, 0], default_config_key='square', movable=True, mass=10)
        self.add_entity(square_01)

        pentagon_01 = Basic([50, 160, 0], default_config_key='pentagon', radius = 15)
        self.add_entity(pentagon_01)

        hexagon_01 = Basic([100, 100, 0], default_config_key='hexagon', graspable = True, mass = 5)
        self.add_entity(hexagon_01)


class Contact_01(SingleRoom):

    def __init__(self, size = (200, 200), **playground_params):

        super(Contact_01, self).__init__(size = size, **playground_params)

        endgoal_01 = VisibleEndGoal([100, 100, 0], reward=50)
        self.add_entity(endgoal_01)

        deathtrap_01 = VisibleDeathTrap([180, 180, 0])
        self.add_entity(deathtrap_01)

        poison = EntityGenerator.create('poison', initial_position = [15,15,0])
        self.add_entity(poison)

        poison_area = PositionAreaSampler(area_shape='rectangle', center=[100, 50], width_length=[20, 20])
        for i in range(5):
            poison = Poison(poison_area)
            self.add_entity(poison)

        candy_area = PositionAreaSampler(area_shape='rectangle', center=[50, 100], width_length=[20, 20])
        for i in range(5):
            candy = Candy(candy_area)
            self.add_entity(candy)

        # outside on purpose
        outside_area = PositionAreaSampler(area_shape='rectangle', center=[200, 100], width_length=[50, 50])
        for i in range(8):
            candy = Candy(outside_area)
            self.add_entity(candy)


class Zones_01(SingleRoom):

    def __init__(self, size = (200, 200), **playground_params):

        super(Zones_01, self).__init__(size = size, **playground_params)

        goal_1 = GoalZone([20, 20, 0])
        self.add_entity(goal_1)

        goal_2 = GoalZone([180, 20, 0])
        self.add_entity(goal_2)

        death_1 = DeathZone([20, 180, 0], reward=-25)
        self.add_entity(death_1)

        death_2 = DeathZone([180, 180, 0])
        self.add_entity(death_2)

        healing_1 = HealingZone([100, 50, 0])
        self.add_entity(healing_1)

        toxic_1 = ToxicZone([50, 100, 0])
        self.add_entity(toxic_1)


class Interactive_01(SingleRoom):

    def __init__(self, size = (300, 300), **playground_params):

        super(Interactive_01, self).__init__(size = size, **playground_params)

        goal_1 = GoalZone([20, 20, 0])
        self.add_entity(goal_1)

        apple = Apple([100, 50, 0])
        self.add_entity(apple)

        rotten = RottenApple([100, 100, 0])
        self.add_entity(rotten)


        area_1 = PositionAreaSampler(area_shape='rectangle', center=[200, 150], width_length=[20, 50])
        dispenser_1 = Dispenser(
            [150, 150, 0],
            entity_produced=Poison,
            production_area=area_1
        )
        self.add_entity(dispenser_1)

        area_2 = PositionAreaSampler(area_shape='gaussian', center=[150, 50], variance = 300, radius=60)
        dispenser_2 = Dispenser(
            [100, 150, 0],
            entity_produced=Candy,
            production_area=area_2
        )
        self.add_entity(dispenser_2)

        dispenser_3 = Dispenser(
            [200, 150, 0],
            entity_produced=Candy,
            entity_produced_params={'radius':3, 'reward':42},
            movable=True,
            mass=5
        )
        self.add_entity(dispenser_3)

        key_chest = Key([50, 200, 0], default_config_key='pentagon', radius = 7, graspable = True, mass = 10)
        self.add_entity(key_chest)

        treasure = Apple([0, 0, 0])
        chest = Chest([100, 200,0.2], key = key_chest, treasure = treasure, width_length = [20, 50])
        self.add_entity(chest)

        coin = Coin([150, 200, 0], graspable=True)
        self.add_entity(coin)

        coin = Coin([150, 220, 0], graspable=True)
        self.add_entity(coin)

        coin = Coin([150, 240, 0], graspable=True)
        self.add_entity(coin)

        vending = VendingMachine([200, 200, 0])
        self.add_entity(vending)


class Doors_01(SingleRoom):

    def __init__(self, size = (300, 200), **playground_params):

        super(Doors_01, self).__init__(size = size, **playground_params)

        goal_1 = GoalZone([20, 20, 0])
        self.add_entity(goal_1)

        door_1 = Door( [100, 130, math.pi/2])
        self.add_entity(door_1)
        switch_1 = OpenCloseSwitch( [100, 30, 0], door = door_1 )
        self.add_entity(switch_1)
        switch_2 = OpenCloseSwitch( [100, 70, 0], door = door_1 )
        self.add_entity(switch_2)

        door_2 = Door( [150, 130, math.pi/2])
        self.add_entity(door_2)

        timerswitch = EntityGenerator.create('timer-switch', initial_position=[150, 70, 0], door=door_2, time_open = 20)
        self.add_entity(timerswitch)

        door_3 = Door([200, 130, math.pi / 2])
        self.add_entity(door_3)

        pushbutton = PushButton( [200, 70, 0], door=door_3)
        self.add_entity(pushbutton)

        door_4 = Door([250, 130, math.pi / 2])
        key = Key( [250, 40, math.pi/2], graspable = True, interaction_range = 5, mass = 30)
        lock = Lock( [250, 70, 0], door = door_4, key = key,  )

        self.add_entity(door_4)
        self.add_entity(key)
        self.add_entity(lock)


class Proximity_01(SingleRoom):

    def __init__(self, size = (200, 200), **playground_params):

        super(Proximity_01, self).__init__(size = size, **playground_params)

        fairy = Fairy([80, 150, 0])
        self.add_entity(fairy)

        fireball = Fireball([150, 80, 0])
        self.add_entity(fireball)

        goal_1 = GoalZone([20, 20, 0])
        self.add_entity(goal_1)


class Fields_01(SingleRoom):

    def __init__(self, size = (200, 200), **playground_params):

        super(Fields_01, self).__init__(size = size, **playground_params)

        area_1 = PositionAreaSampler(area_shape='rectangle', center=[70, 70], width_length=[30, 100])
        field = Field(Poison, None, production_area=area_1)
        self.add_entity(field)

        area_2 = PositionAreaSampler(area_shape='rectangle', center=[200, 70], width_length=[50, 50])
        field = Field(Candy, None, production_area=area_2)
        self.add_entity(field)

        goal_1 = GoalZone([20, 20, 0])
        self.add_entity(goal_1)


class Trajectory_01(SingleRoom):

    def __init__(self, size = (200, 200), **playground_params):

        super(Trajectory_01, self).__init__(size = size, **playground_params)

        trajectory = Trajectory('waypoints', 300, waypoints=[[20, 20], [20, 180], [180,180], [180,20]])
        goal_1 = GoalZone(trajectory)
        self.add_entity(goal_1)

        trajectory = Trajectory('shape', 200, 8, shape='square', center=[100, 70, 0], radius=50)
        fireball = Fireball(trajectory)
        self.add_entity(fireball)

        trajectory = Trajectory('shape', 100, 8, shape='pentagon', center = [50, 150, 0], radius= 30, counter_clockwise = True)
        fireball = Fireball(trajectory)
        self.add_entity(fireball)
