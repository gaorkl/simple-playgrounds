import math

from simple_playgrounds.playgrounds.playground import PlaygroundRegister
from simple_playgrounds.playgrounds.layouts import SingleRoom
from simple_playgrounds.elements.collection.basic import Physical, Traversable
from simple_playgrounds.elements.collection.contact import VisibleEndGoal, VisibleDeathTrap, Poison, Candy
from simple_playgrounds.elements.collection.zone import GoalZone, DeathZone, HealingZone, ToxicZone
from simple_playgrounds.elements.collection.edible import Apple, RottenApple

# pylint: disable=wildcard-import
# pylint: disable=unused-wildcard-import
from simple_playgrounds.common.position_samplers import CoordinateSampler


@PlaygroundRegister.register('test', 'basic')
class Basics(SingleRoom):

    def __init__(self, size=(400, 200), **playground_params):

        super().__init__(size=size, **playground_params)

        rectangle_01 = Physical(config_key='rectangle',  name='test')
        self.add_element(rectangle_01, initial_coordinates=((150, 160), math.pi/4))

        circle_01 = Traversable(config_key='circle',
                          movable=False, mass=100, texture=[150, 150, 150])
        self.add_element(circle_01, ((50, 50), 0))

        square_01 = Physical(config_key='square', movable=True, mass=10)
        self.add_element(square_01, ((150, 60), 0))

        pentagon_01 = Physical(config_key='pentagon', radius=15)
        self.add_element(pentagon_01, ((50, 160), math.pi/2))

        tri_01 = Physical(config_key='triangle',
                          movable=False, mass=5)
        self.add_element(tri_01, ((100, 100), math.pi/4))

        tri_01 = Physical(config_key='triangle',
                          movable=False, mass=5, radius = 20)
        self.add_element(tri_01, ((300, 66), 0))

        tri_01 = Physical(config_key='triangle',
                          movable=False, mass=5, radius = 20 )
        self.add_element(tri_01, ((300, 133), math.pi/3))


@PlaygroundRegister.register('test', 'grasp')
class Graspables(SingleRoom):

    def __init__(self, size=(200, 200), **playground_params):

        super().__init__(size=size, **playground_params)

        rectangle_01 = Physical(config_key='rectangle',
                             graspable=True, mass=10)
        self.add_element(rectangle_01, ((150, 160), 0.2))

        circle_01 = Physical(config_key='circle',
                          graspable=True, mass=10, texture=[150, 150, 150])
        self.add_element(circle_01, ((50, 50), 0))

        square_01 = Physical(config_key='square',
                          graspable=True, mass=10)
        self.add_element(square_01, ((150, 60), math.pi/4))

        pentagon_01 = Physical(config_key='pentagon', radius=15,
                            graspable=True, mass=10)
        self.add_element(pentagon_01, ((50, 160), 0))

        hexagon_01 = Physical(config_key='hexagon',
                           graspable=True, mass=10)
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
                                        center=[100, 150], width_length=[20, 20])
        for _ in range(5):
            poison = Poison()
            self.add_element(poison, poison_area)

        candy_area = CoordinateSampler(area_shape='rectangle',
                                       center=[50, 100], width_length=[20, 20])
        for _ in range(5):
            candy = Candy()
            self.add_element(candy, candy_area)

        # outside on purpose
        outside_area = CoordinateSampler(area_shape='rectangle',
                                         center=[200, 100], width_length=[50, 50])
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

# @PlaygroundRegister.register('test', 'interactives')
# class Interactives(SingleRoom):
#
#     def __init__(self, size=(300, 300), **playground_params):
#
#         super().__init__(size=size, **playground_params)
#
#         goal_1 = GoalZone()
#         self.add_scene_element(goal_1, [(20, 20), 0])
#
#         apple = Apple(physical_shape='pentagon', graspable=True)
#         self.add_scene_element(apple, [(100, 50), 0])
#
#         rotten = RottenApple()
#         self.add_scene_element(rotten, [(100, 100), 0])
#
#         area_1 = CoordinateSampler(area_shape='rectangle',
#                                    center=[200, 150], width_length=[20, 50])
#         dispenser_1 = Dispenser(entity_produced=Poison, production_area=area_1)
#         self.add_scene_element(dispenser_1, [(150, 150), 0])
#
#         area_2 = CoordinateSampler(area_shape='gaussian',
#                                    center=[150, 50], variance=300, radius=60)
#         dispenser_2 = Dispenser(entity_produced=Candy, production_area=area_2)
#         self.add_scene_element(dispenser_2, [(100, 150), 0])
#
#         dispenser_3 = Dispenser(
#             entity_produced=Candy,
#             entity_produced_params={'radius': 3, 'reward': 42},
#             movable=True,
#             mass=5
#         )
#         self.add_scene_element(dispenser_3, [(200, 150), 0])
#
#         key_chest = Key(config_key='pentagon',
#                         radius=7, graspable=True, mass=10)
#         self.add_scene_element(key_chest, [(50, 200), 0])
#
#         treasure = Apple()
#         chest = Chest(key=key_chest, treasure=treasure, width_length=[20, 50])
#         self.add_scene_element(chest, [(100, 200), 0.2])
#
#         vending = VendingMachine()
#         self.add_scene_element(vending, [(200, 200), 0])
#
#         coin = Coin(graspable=True, vending_machine=vending)
#         self.add_scene_element(coin, [(150, 200), 0])
#
#         coin = Coin(graspable=True, vending_machine=vending)
#         self.add_scene_element(coin, [(150, 220), 0])
#
#         coin = Coin(graspable=True, vending_machine=vending)
#         self.add_scene_element(coin, [(150, 240), 0])


#
# @PlaygroundRegister.register('test', 'conditioning')
# class Conditioning(SingleRoom):
#
#     def __init__(self, size=(300, 300), **playground_params):
#
#         super().__init__(size=size, **playground_params)
#
#         lever = Lever()
#         self.add_scene_element(lever, [(100, 50), 0])
#
#         light_01 = ConditionedColorChanging(conditioned_entity=lever,
#                                             timers=[100, 100],
#                                             textures=[[100, 200, 0], [200, 100, 200]])
#         self.add_scene_element(light_01, [(150, 100), 0])
#
#
# @PlaygroundRegister.register('test', 'doors')
# class Doors(SingleRoom):
#
#     def __init__(self, size=(300, 300), **playground_params):
#
#         super().__init__(size=size, **playground_params)
#
#         door_1 = Door()
#         self.add_scene_element(door_1, [(100, 150), math.pi/2])
#         switch_1 = OpenCloseSwitch(door=door_1)
#         self.add_scene_element(switch_1, [(100, 50), 0])
#
#         door_2 = Door()
#         self.add_scene_element(door_2, [(150, 150), math.pi/2])
#
#         timerswitch = TimerSwitch(door=door_2, time_open=20)
#         self.add_scene_element(timerswitch, [(150, 90), 0])
#
#         door_3 = Door()
#         self.add_scene_element(door_3, [(200, 150), math.pi / 2])
#
#         pushbutton = PushButton(door=door_3)
#         self.add_scene_element(pushbutton, [(200, 90), 0])
#
#         door_4 = Door()
#         key = Key(graspable=True, interaction_range=5, mass=10)
#         lock = Lock(door=door_4, key=key)
#
#         self.add_scene_element(door_4, [(250, 150), math.pi / 2])
#         self.add_scene_element(key, [(250, 60), math.pi/2])
#         self.add_scene_element(lock, [(250, 90), 0])
#
#
# @PlaygroundRegister.register('test', 'teleports')
# class Teleports(SingleRoom):
#
#     def __init__(self, size=(300, 300), **playground_params):
#
#         super().__init__(size=size, **playground_params)
#
#         teleport_1 = Teleport(radius=10, physical_shape='circle')
#         target_1 = Traversable(radius=10, config_key='circle')
#         teleport_1.add_target(target_1)
#         self.add_scene_element(teleport_1, [(50, 50), 0])
#         self.add_scene_element(target_1, [(250, 50), 0])
#
#         teleport_2 = Teleport(radius=10, physical_shape='circle')
#         target_2 = Basic(radius=20, config_key='circle')
#         teleport_2.add_target(target_2)
#         self.add_scene_element(teleport_2, [(50, 150), 0])
#         self.add_scene_element(target_2, [(250, 150), 0])
#
#         teleport_3 = Teleport(radius=10, physical_shape='circle')
#         teleport_4 = Teleport(radius=10, physical_shape='circle')
#         teleport_3.add_target(teleport_4)
#         teleport_4.add_target(teleport_3)
#         self.add_scene_element(teleport_3, [(50, 250), 0])
#         self.add_scene_element(teleport_4, [(250, 250), 0])
#
#
# @PlaygroundRegister.register('test', 'xteleports')
# class ExtraTeleports(SingleRoom):
#
#     def __init__(self, size=(300, 300), **playground_params):
#
#         super().__init__(size=size, **playground_params)
#
#         for x in range(50, 250, 50):
#             for y in range(50, 250, 50):
#
#                 teleport_1 = Teleport(radius=10, physical_shape='circle')
#                 target_1 = Traversable(radius=10, config_key='circle')
#                 teleport_1.add_target(target_1)
#                 self.add_scene_element(teleport_1, [(x, y), 0])
#                 self.add_scene_element(target_1, [(x+25, y+25), 0])
#
#
#
# @PlaygroundRegister.register('test', 'proximity')
# class Proximity(SingleRoom):
#
#     def __init__(self, size=(200, 200), **playground_params):
#
#         super().__init__(size=size, **playground_params)
#
#         fairy = Fairy()
#         self.add_scene_element(fairy, [(80, 150), 0])
#
#         fireball = Fireball()
#         self.add_scene_element(fireball, [(150, 80), 0])
#
#         goal_1 = GoalZone()
#         self.add_scene_element(goal_1, [(20, 20), 0])
#
#
# @PlaygroundRegister.register('test', 'fields')
# class Fields(SingleRoom):
#
#     def __init__(self, size=(200, 200), **playground_params):
#
#         super().__init__(size=size, **playground_params)
#
#         area_1 = CoordinateSampler(area_shape='rectangle',
#                                    center=[70, 70], width_length=[30, 100])
#         field = Field(Poison, production_area=area_1)
#         self.add_scene_element(field)
#
#         area_2 = CoordinateSampler(area_shape='rectangle',
#                                    center=[200, 70], width_length=[50, 50])
#         field = Field(Candy, production_area=area_2)
#         self.add_scene_element(field)
#
#
# @PlaygroundRegister.register('test', 'trajectories')
# class Trajectories(SingleRoom):
#
#     def __init__(self, size=(200, 200), **playground_params):
#
#         super().__init__(size=size, **playground_params)
#
#         trajectory = Trajectory('waypoints', trajectory_duration=300,
#                                 waypoints=[[20, 20], [20, 180], [180, 180], [180, 20]])
#         goal_1 = GoalZone()
#         self.add_scene_element(goal_1, trajectory)
#
#         trajectory = Trajectory('shape', trajectory_duration=200, n_rotations=8,
#                                 shape='square', center=[100, 70, 0], radius=50)
#         fireball = Fireball()
#         self.add_scene_element(fireball, trajectory)
#
#         trajectory = Trajectory('shape', trajectory_duration=100, n_rotations=8,
#                                 shape='pentagon', center=[50, 150, 0], radius=30,
#                                 counter_clockwise=True)
#         fireball = Fireball()
#         self.add_scene_element(fireball, trajectory)
