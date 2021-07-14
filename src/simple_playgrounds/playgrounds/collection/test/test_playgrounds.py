import math

from ...playground import PlaygroundRegister
from ...layouts import GridRooms, SingleRoom
from ....elements.collection.basic import Physical, Traversable
from ....elements.collection.zone import DeathZone, GoalZone, HealingZone, ToxicZone
from ....elements.collection.edible import Apple, RottenApple
from ....elements.collection.activable import Dispenser, VendingMachine, Chest, RewardOnActivation, OpenCloseSwitch, TimerSwitch, Lock
from ....elements.collection.gem import Key, Coin
from ....elements.collection.conditioning import RewardFlipper
from ....elements.collection.contact import VisibleEndGoal, VisibleDeathTrap, Poison, Candy
from ....elements.collection.teleport import VisibleBeamHoming, InvisibleBeam, Portal, PortalColor
from ....elements.collection.proximity import Fairy, Fireball


from ....common.position_utils import CoordinateSampler, Trajectory
from ....common.timer import Timer

from ....elements.field import Field


@PlaygroundRegister.register('test', 'basic')
class Basics(SingleRoom):
    def __init__(self, size=(400, 200), **playground_params):

        super().__init__(size=size, **playground_params)

        rectangle_01 = Physical(config_key='rectangle', name='test')
        self.add_element(rectangle_01,
                         initial_coordinates=((150, 160), math.pi / 4))

        circle_01 = Traversable(config_key='circle',
                                movable=False,
                                mass=100,
                                texture=[150, 150, 150])
        self.add_element(circle_01, ((50, 50), 0))

        square_01 = Physical(config_key='square', movable=True, mass=10)
        self.add_element(square_01, ((150, 60), 0))

        pentagon_01 = Physical(config_key='pentagon', radius=15)
        self.add_element(pentagon_01, ((50, 160), math.pi / 2))

        tri_01 = Physical(config_key='triangle', movable=False, mass=5)
        self.add_element(tri_01, ((100, 100), math.pi / 4))

        tri_01 = Physical(config_key='triangle',
                          movable=False,
                          mass=5,
                          radius=20)
        self.add_element(tri_01, ((300, 66), 0))

        tri_01 = Physical(config_key='triangle',
                          movable=False,
                          mass=5,
                          radius=20)
        self.add_element(tri_01, ((300, 133), math.pi / 3))


@PlaygroundRegister.register('test', 'grasp')
class Graspables(SingleRoom):
    def __init__(self, size=(200, 200), **playground_params):

        super().__init__(size=size, **playground_params)

        rectangle_01 = Physical(config_key='rectangle',
                                graspable=True,
                                mass=10)
        self.add_element(rectangle_01, ((150, 160), 0.2))

        circle_01 = Physical(config_key='circle',
                             graspable=True,
                             mass=10,
                             texture=[150, 150, 150])
        self.add_element(circle_01, ((50, 50), 0))

        square_01 = Physical(config_key='square', graspable=True, mass=10)
        self.add_element(square_01, ((150, 60), math.pi / 4))

        pentagon_01 = Physical(config_key='pentagon',
                               radius=15,
                               graspable=True,
                               mass=10)
        self.add_element(pentagon_01, ((50, 160), 0))

        hexagon_01 = Physical(config_key='hexagon', graspable=True, mass=10)
        self.add_element(hexagon_01, ((100, 100), 0))


@PlaygroundRegister.register('test', 'contacts')
class Contacts(SingleRoom):
    def __init__(self, size=(200, 200), **playground_params):

        super().__init__(size=size, **playground_params)

        endgoal_01 = VisibleEndGoal(reward=50)
        self.add_element(endgoal_01, ((20, 180), 0))

        deathtrap_01 = VisibleDeathTrap()
        self.add_element(deathtrap_01, ((180, 180), 0))

        poison = Poison()
        self.add_element(poison, ((15, 15), 0))

        poison_area = CoordinateSampler(area_shape='rectangle',
                                        center=(100, 150),
                                        size=(20, 20))
        for _ in range(5):
            poison = Poison()
            self.add_element(poison, poison_area)

        candy_area = CoordinateSampler(area_shape='rectangle',
                                       center=(50, 100),
                                       size=(20, 20))
        for _ in range(5):
            candy = Candy()
            self.add_element(candy, candy_area)

        # outside on purpose
        outside_area = CoordinateSampler(area_shape='rectangle',
                                         center=(200, 100),
                                         size=(50, 50))
        for _ in range(8):
            candy = Candy()
            self.add_element(candy, outside_area)


@PlaygroundRegister.register('test', 'zones')
class Zones(SingleRoom):
    def __init__(self, size=(200, 200), **playground_params):

        super().__init__(size=size, **playground_params)

        goal_1 = GoalZone(100)
        self.add_element(goal_1, ((20, 20), 0))

        goal_2 = GoalZone(150)
        self.add_element(goal_2, ((180, 20), 0))

        death_1 = DeathZone(-25)
        self.add_element(death_1, ((20, 180), 0))

        death_2 = DeathZone(-40)
        self.add_element(death_2, ((180, 180), 0))

        healing_1 = HealingZone(5, 100)
        self.add_element(healing_1, ((50, 100), 0))

        toxic_1 = ToxicZone(-5, 100)
        self.add_element(toxic_1, ((150, 100), 0))


@PlaygroundRegister.register('test', 'edibles')
class Edibles(SingleRoom):
    def __init__(self, size=(200, 200), **playground_params):

        super().__init__(size=size, **playground_params)

        apple = Apple(10, min_reward=1)
        self.add_element(apple, ((50, 100), 0))

        apple = Apple(20, 1, shrink_ratio=0.5)
        self.add_element(apple, ((50, 50), 0))

        rotten = RottenApple(-20, -1, graspable=True)
        self.add_element(rotten, ((100, 100), 0))

        rotten = RottenApple(-20, -5)
        self.add_element(rotten, ((100, 100), 0))


@PlaygroundRegister.register('test', 'dispensers')
class Dispensers(SingleRoom):
    def __init__(self, size=(200, 400), **playground_params):

        super().__init__(size=size, **playground_params)

        x_dispenser = 50
        x_area = 150

        # Dispenser on Area
        area = CoordinateSampler(area_shape='rectangle',
                                 center=(x_area, 50),
                                 size=(20, 60),
                                 angle=math.pi / 3)
        dispenser = Dispenser(
            element_produced=Poison,
            element_produced_params={'reward': -5},
            production_area=area,
            production_limit=20,
        )
        self.add_element(dispenser, ((x_dispenser, 50), 0))

        # Dispenser on Area
        area = CoordinateSampler(area_shape='circle',
                                 center=(x_area, 100),
                                 radius=30)
        dispenser = Dispenser(
            element_produced=Poison,
            element_produced_params={'reward': -5},
            production_area=area,
        )
        self.add_element(dispenser, ((x_dispenser, 100), 0))

        # Dispenser on Area
        area = CoordinateSampler(area_shape='circle',
                                 center=(x_area, 150),
                                 radius=50,
                                 min_radius=30)
        dispenser = Dispenser(
            element_produced=Candy,
            element_produced_params={'reward': 5},
            production_area=area,
        )
        self.add_element(dispenser, ((x_dispenser, 150), 0))

        # Dispenser on Area
        area = CoordinateSampler(area_shape='gaussian',
                                 center=(x_area, 200),
                                 std=30,
                                 radius=60)
        dispenser = Dispenser(
            element_produced=Poison,
            element_produced_params={'reward': -5},
            production_area=area,
        )
        self.add_element(dispenser, ((x_dispenser, 200), 0))

        # Dispenser on Area
        area = CoordinateSampler(area_shape='gaussian',
                                 center=(x_area, 250),
                                 std=40,
                                 radius=60,
                                 min_radius=20)
        dispenser = Dispenser(
            element_produced=Candy,
            element_produced_params={'reward': 5},
            production_area=area,
        )
        self.add_element(dispenser, ((x_dispenser, 250), 0))

        # Dispenser on Dispenser

        dispenser = Dispenser(element_produced=Candy,
                              element_produced_params={'reward': 5},
                              production_range=20,
                              graspable=True)
        self.add_element(dispenser, ((x_dispenser, 300), 0))

        # Dispenser on Element

        pentagon_01 = Physical(config_key='pentagon',
                               radius=15,
                               graspable=True,
                               mass=5)
        self.add_element(pentagon_01, ((x_area, 350), math.pi / 2))

        dispenser = Dispenser(element_produced=Candy,
                              element_produced_params={'reward': 5},
                              production_range=20,
                              production_area=pentagon_01)
        self.add_element(dispenser, ((x_dispenser, 350), 0))


@PlaygroundRegister.register('test', 'gems')
class Gems(SingleRoom):
    def __init__(self, size=(200, 200), **playground_params):
        super().__init__(size=size, **playground_params)

        x_gem = 50
        x_activable = 100

        treasure = Apple()

        chest = Chest(treasure=treasure,
                      size=[20, 50])

        self.add_element(chest, ((x_activable, 50), 0))

        key_chest = Key(mass=10,
                        locked_elem=chest,
                        graspable=True,
                        )
        self.add_element(key_chest, ((x_gem, 50), 0))

        vending = VendingMachine(quantity_rewards=3, reward=10)
        self.add_element(vending, ((x_activable, 100), 0))

        coin = Coin(graspable=True, vending_machine=vending)
        self.add_element(coin, ((x_gem, 100), 0))

        coin = Coin(graspable=True, vending_machine=vending)
        self.add_element(coin, ((x_gem, 120), 0))

        coin = Coin(graspable=True, vending_machine=vending)
        self.add_element(coin, ((x_gem, 140), 0))

        coin = Coin(graspable=True, vending_machine=vending)
        self.add_element(coin, ((x_gem, 160), 0))


@PlaygroundRegister.register('test', 'conditioning')
class Conditioning(SingleRoom):

    def __init__(self, size=(200, 200), **playground_params):

        super().__init__(size=size, **playground_params)

        roa = RewardOnActivation(reward=10)
        self.add_element(roa, ((50, 50), 0))

        light_01 = RewardFlipper(element_flipped=roa,
                                 textures=[(100, 200, 0), (200, 100, 200)],
                                 activable_by_agent=True)
        self.add_element(light_01, ((100, 50), 0))

        roa = RewardOnActivation(reward=10)
        self.add_element(roa, ((50, 150), 0))

        light_02 = RewardFlipper(element_flipped=roa,
                                 textures=[(100, 200, 0), (200, 100, 200)],
                                 activable_by_agent=True)
        self.add_element(light_02, ((100, 150), 0))

        timer = Timer([100, 50])
        self.add_timer(timer, light_02)


@PlaygroundRegister.register('test', 'doors')
class Doors(GridRooms):

    def __init__(self, size=(300, 300), **playground_params):

        super().__init__(size=size, room_layout=(2, 2),
                         doorstep_size=40, **playground_params)

        doorstep_1 = self.grid_rooms[0][0].doorstep_right
        door_1 = doorstep_1.generate_door()
        self.add_element(door_1)

        switch_1 = OpenCloseSwitch(door=door_1)
        self.add_element(switch_1, self.grid_rooms[0][0].get_random_position_on_wall('right', switch_1))

        doorstep_2 = self.grid_rooms[0][0].doorstep_down
        door_2 = doorstep_2.generate_door()
        self.add_element(door_2)

        timer = Timer(durations=100)
        switch_2 = TimerSwitch(door=door_2, timer=timer)
        self.add_element(switch_2, self.grid_rooms[0][0].get_random_position_on_wall('down', switch_2))
        self.add_timer(timer, switch_2)

        doorstep_3 = self.grid_rooms[0][1].doorstep_right
        door_3 = doorstep_3.generate_door()
        self.add_element(door_3)

        lock = Lock(door=door_3)
        self.add_element(lock, self.grid_rooms[0][1].get_random_position_on_wall('left', lock))

        key = Key(locked_elem=lock)
        center, size = self.grid_rooms[0][1].get_partial_area('left-down')
        area_sampler = CoordinateSampler(center=center, size=size, area_shape='rectangle')
        self.add_element(key, area_sampler)


@PlaygroundRegister.register('test', 'teleports')
class Teleports(SingleRoom):

    def __init__(self, size=(300, 700), **playground_params):

        super().__init__(size=size, **playground_params)

        pos_left = (100, 100)
        pos_right = (200, 100)
        vis_beam = InvisibleBeam(destination=(pos_right, math.pi))
        self.add_element(vis_beam, (pos_left, 0))

        pos_left = pos_left[0], pos_left[1] + 100
        pos_right = pos_right[0], pos_right[1] + 100
        coord_sampler = CoordinateSampler(pos_right, area_shape='circle', radius=20)
        vis_beam = InvisibleBeam(destination=coord_sampler, keep_inertia=False)
        self.add_element(vis_beam, (pos_left, 0))

        pos_left = pos_left[0], pos_left[1] + 100
        pos_right = pos_right[0], pos_right[1] + 100
        target = Physical(config_key='circle', radius=5)
        self.add_element(target, (pos_right, 0))
        homing = VisibleBeamHoming(destination=target, keep_inertia=True, relative_teleport=False)
        self.add_element(homing, (pos_left, math.pi))

        pos_left = pos_left[0], pos_left[1] + 100
        pos_right = pos_right[0], pos_right[1] + 100
        target = Physical(config_key='circle', radius=5)
        self.add_element(target, (pos_right, math.pi/2))
        homing = VisibleBeamHoming(destination=target, relative_teleport=True, keep_inertia=False)
        self.add_element(homing, (pos_left, 0))

        pos_left = pos_left[0], pos_left[1] + 100
        pos_right = pos_right[0], pos_right[1] + 100
        target = Traversable(config_key='circle', radius=10)
        self.add_element(target, (pos_right, math.pi / 2))
        homing = VisibleBeamHoming(destination=target, relative_teleport=True, keep_inertia=False)
        self.add_element(homing, (pos_left, 0))

        pos_left = pos_left[0]-90, pos_left[1] + 100
        pos_right = pos_right[0]+90, pos_right[1] + 100
        portal_red = Portal(color=PortalColor.RED)
        self.add_element(portal_red, (pos_left, 0))
        portal_blue = Portal(color=PortalColor.BLUE)
        self.add_element(portal_blue, (pos_right, math.pi))

        portal_red.destination = portal_blue
        portal_blue.destination = portal_red


@PlaygroundRegister.register('test', 'proximity')
class Proximals(SingleRoom):

    def __init__(self, size=(200, 200), **playground_params):

        super().__init__(size=size, **playground_params)

        fairy = Fairy(reward=20, limit = 200)
        self.add_element(fairy, ((80, 150), 0))

        fireball = Fireball(reward = -10)
        self.add_element(fireball, ((150, 80), 0))


@PlaygroundRegister.register('test', 'fields')
class Fields(SingleRoom):

    def __init__(self, size=(200, 200), **playground_params):

        super().__init__(size=size, **playground_params)

        area_1 = CoordinateSampler(area_shape='rectangle',
                                   center=(70, 70), size=(30, 100))
        field = Field(Poison, production_area=area_1)
        self.add_field(field)

        area_2 = CoordinateSampler(area_shape='rectangle',
                                   center=(200, 70), size=(50, 50))
        field = Field(Candy, production_area=area_2)
        self.add_field(field)


@PlaygroundRegister.register('test', 'trajectories')
class Trajectories(SingleRoom):

    def __init__(self, size=(200, 200), **playground_params):

        super().__init__(size=size, **playground_params)

        trajectory = Trajectory('waypoints', trajectory_duration=300,
                                waypoints=[[20, 20], [20, 180], [180, 180], [180, 20]])
        goal_1 = GoalZone(10)
        self.add_element(goal_1, trajectory)

        trajectory = Trajectory('shape', trajectory_duration=200, n_rotations=8,
                                shape='square', center=[100, 70, 0], radius=50)
        fireball = Fireball(-2)
        self.add_element(fireball, trajectory)

        trajectory = Trajectory('shape', trajectory_duration=100, n_rotations=8,
                                shape='pentagon', center=[50, 150, 0], radius=30,
                                counter_clockwise=True)
        fireball = Fireball(-3)
        self.add_element(fireball, trajectory)


@PlaygroundRegister.register('test', 'xteleports')
class ExtraTeleports(SingleRoom):

    def __init__(self, size=(400, 400), **playground_params):

        super().__init__(size=size, **playground_params)

        for x in range(50, 350, 100):
            for y in range(50, 350, 100):

                target = Traversable(config_key='circle', radius=10)
                self.add_element(target, ((300 - x+50, 300 - y+50), 0))
                homing = VisibleBeamHoming(radius=10, destination=target, relative_teleport=True, keep_inertia=False)
                self.add_element(homing, ((x, y), 0))
