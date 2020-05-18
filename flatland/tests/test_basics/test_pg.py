from flatland.playgrounds.playground import PlaygroundGenerator, Playground
from flatland.playgrounds.collection.empty import Room
from flatland.utils.position_utils import PositionAreaSampler, Trajectory
from flatland.entities import *
import math

@PlaygroundGenerator.register_subclass('basic_01')
class Basic_01(Room):

    def __init__(self, scene_params):

        super(Basic_01, self).__init__(scene_params)

        rectangle_01 = Basic([150, 160, 0.2], default_config_key='rectangle')
        self.add_entity(rectangle_01)

        circle_01 = Basic([50, 60, 0], default_config_key='circle', movable=True, mass=100, texture=[150, 150, 150])
        self.add_entity(circle_01)

        square_01 = Basic([150, 60, 0], default_config_key='square', movable=True, mass=10)
        self.add_entity(square_01)

        pentagon_01 = Basic([50, 160, 0], default_config_key='pentagon', radius = 15)
        self.add_entity(pentagon_01)

        hexagon_01 = Basic([100, 100, 0], default_config_key='hexagon', graspable = True, mass = 5)
        self.add_entity(hexagon_01)



@PlaygroundGenerator.register_subclass('contact_01')
class Contact_01(Room):

    def __init__(self, scene_params=None):

        super(Contact_01, self).__init__(scene_params)

        endgoal_01 = VisibleEndGoal([100, 100, 0], reward=50)
        self.add_entity(endgoal_01)

        deathtrap_01 = VisibleDeathTrap([180, 180, 0])
        self.add_entity(deathtrap_01)

        poison = Poison([15,15,0])
        self.add_entity(poison)

        poison_area = PositionAreaSampler(area_shape='rectangle', center=[100, 50], shape=[20, 20])
        for i in range(5):
            poison = Poison(poison_area)
            self.add_entity(poison)

        candy_area = PositionAreaSampler(area_shape='rectangle', center=[50, 100], shape=[20, 20])
        for i in range(5):
            candy = Candy(candy_area)
            self.add_entity(candy)

        # outside on purpose
        outside_area = PositionAreaSampler(area_shape='rectangle', center=[200, 100], shape=[50, 50])
        for i in range(8):
            candy = Candy(outside_area)
            self.add_entity(candy)


@PlaygroundGenerator.register_subclass('zones_01')
class Zones_01(Room):

    def __init__(self, scene_params=None):

        scene_params['room_shape'] = [200, 200]

        super(Zones_01, self).__init__(scene_params)

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


@PlaygroundGenerator.register_subclass('interactive_01')
class Interactive_01(Room):

    def __init__(self, scene_params = None):

        scene_params['room_shape'] = [300,300]

        super(Interactive_01, self).__init__(scene_params)

        goal_1 = GoalZone([20, 20, 0])
        self.add_entity(goal_1)

        apple = Apple([100, 50, 0])
        self.add_entity(apple)

        rotten = RottenApple([100, 100, 0])
        self.add_entity(rotten)


        area_1 = PositionAreaSampler(area_shape='rectangle', center=[200, 150], shape=[20, 50])
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
        chest = Chest([100, 200,0], key = key_chest, treasure = treasure)
        self.add_entity(chest)

        coin = Coin([150, 200, 0], graspable=True)
        self.add_entity(coin)

        coin = Coin([150, 220, 0], graspable=True)
        self.add_entity(coin)

        coin = Coin([150, 240, 0], graspable=True)
        self.add_entity(coin)

        vending = VendingMachine([200, 200, 0])
        self.add_entity(vending)


@PlaygroundGenerator.register_subclass('doors_01')
class Doors_01(Room):

    def __init__(self, scene_params=None):

        scene_params['room_shape'] = [300, 200]

        super(Doors_01, self).__init__(scene_params)

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

        timerswitch = TimerSwitch( [150, 70, 0], door = door_2, time_open = 20)
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



@PlaygroundGenerator.register_subclass('proximity_01')
class Proximity_01(Room):

    def __init__(self, scene_params=None):

        super(Proximity_01, self).__init__(scene_params)

        fairy = Fairy([80, 150, 0])
        self.add_entity(fairy)

        fireball = Fireball([150, 80, 0])
        self.add_entity(fireball)

        goal_1 = GoalZone([20, 20, 0])
        self.add_entity(goal_1)



@PlaygroundGenerator.register_subclass('field_01')
class Fields_01(Room):

    def __init__(self, scene_params=None):


        super(Fields_01, self).__init__(scene_params)

        area_1 = PositionAreaSampler(area_shape='rectangle', center=[70, 70], shape=[30, 100])
        field = Field(Poison, None, production_area=area_1)
        self.add_entity(field)

        area_2 = PositionAreaSampler(area_shape='rectangle', center=[200, 70], shape=[50, 50])
        field = Field(Candy, None, production_area=area_2)
        self.add_entity(field)

        goal_1 = GoalZone([20, 20, 0])
        self.add_entity(goal_1)

@PlaygroundGenerator.register_subclass('trajectory_01')
class Trajectory_01(Room):

    def __init__(self, scene_params=None):


        super(Trajectory_01, self).__init__(scene_params)

        trajectory = Trajectory('waypoints', 300, waypoints=[[20, 20], [20, 180], [180,180], [180,20]])
        goal_1 = GoalZone(trajectory)
        self.add_entity(goal_1)

        # trajectory = Trajectory('waypoints', 300, 4, waypoints=[[50,50], [150,150]])
        # fairy = Fairy([0,0,0], trajectory = trajectory)
        # self.add_entity(fairy)

        trajectory = Trajectory('shape', 200, 8, shape='square', center=[100, 70, 0], radius=50)
        fireball = Fireball(trajectory)
        self.add_entity(fireball)

        trajectory = Trajectory('shape', 100, 8, shape='pentagon', center = [50, 150, 0], radius= 30, counter_clockwise = True)
        fireball = Fireball(trajectory)
        self.add_entity(fireball)

#
# @PlaygroundGenerator.register_subclass('david')
# class David(Playground):
#
#     def __init__(self, params):
#         scenes_params = {
#             'scene': {
#                 'scene_type': 'room',
#                 'room_shape': [200, 200]
#             },
#         }
#
#         params = {**scenes_params, **params}
#
#         super(David, self).__init__(params)
#
#         ### Basic entities
#         basic_1 = basic_default.copy()
#         basic_1['position'] = {
#             'type': 'fixed',
#             'coordinates': [150, 160, 0.56]
#             }
#
#         basic_1['physical_shape'] = 'rectangle'
#         basic_1['shape_rectangle'] = [20, 40]
#
#         basic_2 = basic_default.copy()
#         basic_2['position'] = {
#             'type': 'fixed',
#             'coordinates': [160, 40, math.pi / 7]
#         }
#         basic_2['physical_shape'] = 'rectangle'
#         basic_2['shape_rectangle'] = [30, 40]
#         basic_2['texture'] = {
#             'type': 'random_tiles',
#             'min': [50, 50, 150],
#             'max': [60, 100, 190],
#             'size_tiles': 4
#         }
#
#         basic_3 = basic_default.copy()
#         basic_3['position'] =  {
#             'type': 'fixed',
#             'coordinates':[60, 170, 0.5]}
#
#         basic_3['physical_shape'] = 'pentagon'
#         basic_3['radius'] = 20
#         basic_3['movable'] = True
#         basic_3['texture'] = {
#             'type': 'polar_stripes',
#             'color_1': [0, 50, 150],
#             'color_2': [0, 100, 190],
#             'n_stripes': 4
#         }
#
#         basic_4 = basic_default.copy()
#         basic_4['position'] =  {
#             'type': 'rectangle',
#             'x_range':[40, 80],
#             'y_range':[60, 90],
#             'angle_range': [0.5, 1.9]}
#
#         basic_4['physical_shape'] = 'circle'
#         basic_4['radius'] = 5
#         basic_4['movable'] = True
#
#         for ent in [basic_1, basic_2, basic_3, basic_4]:
#
#             self.add_entity(ent)
#
#
#
#
#
#
#
# @PlaygroundGenerator.register_subclass('chest-test')
# class ChestTest(Playground):
#
#     def __init__(self, params):
#         scenes_params = {
#             'scene': {
#                 'scene_type': 'room',
#                 'scene_shape': [200, 200]
#             },
#         }
#
#         params = {**scenes_params, **params}
#
#         super(ChestTest, self).__init__(params)
#
#         end_zone = end_zone_default.copy()
#         end_zone['position'] = [20, self.width - 20, 0]
#         end_zone['physical_shape'] = 'rectangle'
#         end_zone['shape_rectangle'] = [20, 20]
#         end_zone['reward'] = 50
#         self.add_entity(end_zone)
#
#         ### Basic entities
#         pod = chest_default.copy()
#         pod['position'] = [100, 100, math.pi / 4]
#         pod['key_pod']['position'] = [30, 30, 0]
#
#         self.add_entity(pod)
#
#         self.starting_ {
#             'type': 'rectangle',
#             'x_range': [50, 150],
#             'y_range': [50, 150],
#             'angle_range': [0, 3.14 * 2],
#         }
#
# @PlaygroundGenerator.register_subclass('basic-test')
# class BasicTest(Playground):
#
#     def __init__(self, params):
#
#         scenes_params = {
#             'scene': {
#                 'scene_type': 'room',
#                 'scene_shape': [200, 200]
#             },
#         }
#
#         params = {**scenes_params, **params}
#
#         super(BasicTest, self).__init__(params)
#
#         end_zone = end_zone_default.copy()
#         end_zone['position'] = [20, self.width - 20, 0]
#         end_zone['physical_shape'] = 'rectangle'
#         end_zone['shape_rectangle'] = [20, 20]
#         end_zone['reward'] = 50
#         self.add_entity(end_zone)
#
#         ### Basic entities
#         pod = chest_default.copy()
#         pod['position'] = [100, 100, math.pi / 4]
#         pod['key_pod']['position'] = [30, 30, 0]
#
#         self.add_entity(pod)
#
#         self.starting_ {
#             'type': 'rectangle',
#             'x_range': [50, 150],
#             'y_range': [50, 150],
#             'angle_range': [0, 3.14 * 2],
#         }
#
#
# @PlaygroundGenerator.register_subclass('all-test')
# class AllTest(Playground):
#
#     def __init__(self, params):
#         scenes_params = {
#             'scene': {
#                 'scene_type': 'room',
#                 'room_shape': [600, 800]
#             },
#         }
#
#         params = {**scenes_params, **params}
#
#         super(AllTest, self).__init__(params)
#
#         ### Basic entities
#         basic_1 = basic_default.copy()
#         basic_1['position'] = [350, 250, math.pi / 2]
#         basic_1['physical_shape'] = 'rectangle'
#         basic_1['shape_rectangle'] = [20, 100]
#
#         basic_2 = basic_default.copy()
#         basic_2['position'] = [200, 100, math.pi / 2]
#         basic_2['physical_shape'] = 'rectangle'
#         basic_2['shape_rectangle'] = [30, 100]
#
#         basic_2['texture'] = {
#             'type': 'polar_stripes',
#             'color_1': [150, 0, 50],
#             'color_2': [200, 0, 100],
#             'n_stripes': 4
#         }
#         basic_3 = basic_default.copy()
#         basic_3['position'] = [100, 150, 0]
#         basic_3['physical_shape'] = 'pentagon'
#         basic_3['radius'] = 20
#         basic_3['movable'] = True
#         basic_3['texture'] = {
#             'type': 'polar_stripes',
#             'color_1': [0, 50, 150],
#             'color_2': [0, 100, 190],
#             'n_stripes': 2
#         }
#         ###### Absorbable
#         absorbable_1 = absorbable_default.copy()
#         absorbable_1['position'] = [100, 200, 0.2]
#         absorbable_2 = absorbable_default.copy()
#         absorbable_2['position'] = [100, 250, 0.5]
#         ### Edible
#         edible_1 = edible_default.copy()
#         edible_1['position'] = [100, 300, 0.2]
#         edible_1['physical_shape'] = 'rectangle'
#         edible_1['shape_rectangle'] = [50, 60]
#         edible_1['texture']['type'] = 'polar_stripes'
#         edible_1['texture']['color_1'] = [100, 0, 150]
#         edible_1['texture']['color_2'] = [0, 0, 250]
#         edible_1['texture']['n_stripes'] = 3
#         # edible_1['mass'] = 100
#         # edible_1['movable'] = True
#         # edible_1['graspable'] = True
#         ### Dispenser
#         dispenser_1 = dispenser_default.copy()
#         dispenser_1['position'] = [100, 350, 0]
#         dispenser_1['area'] = [[200, 325], [250, 375]]
#         dispenser_1['limit'] = 7
#
#
#         ### Yielder
#         yielder_1 = yielder_default.copy()
#         yielder_1['area'] = [[100, 400], [200, 500]]
#
#         ### Zone
#         end_zone = end_zone_default.copy()
#         end_zone['position'] = [500, 50, 0]
#         end_zone['physical_shape'] = 'rectangle'
#         end_zone['shape_rectangle'] = [50, 50]
#
#         healing_zone = healing_zone_default.copy()
#         healing_zone['position'] = [500, 100, 0]
#         healing_zone['visible'] = True
#
#         damaging_zone = damaging_zone_default.copy()
#         damaging_zone['position'] = [500, 150, 0]
#
#         contact_endzone = contact_endzone_default.copy()
#         contact_endzone['position'] = [500, 550, 0]
#
#         ##### Button door
#         button_door_1 = button_door_openclose_default.copy()
#         button_door_1['position'] = [600, 200, 0]
#         button_door_1['door']['position'] = [600, 250, math.pi / 2]
#
#         ##### Button door
#         button_door_2 = button_door_opentimer_default.copy()
#         button_door_2['position'] = [600, 350, 0]
#         button_door_2['door']['position'] = [600, 400, math.pi / 2]
#         button_door_2['time_limit'] = 100
#
#         ##### Lock_key door
#         lock_key_door = lock_key_door_default.copy()
#         lock_key_door['position'] = [600, 500, 0]
#         lock_key_door['door']['position'] = [600, 550, math.pi / 2]
#         lock_key_door['key']['position'] = [600, 450, math.pi / 2]
#
#         ##### Moving object
#         moving_1 = basic_default.copy()
#         moving_1['position'] = [500, 500, math.pi / 2]
#         moving_1['trajectory'] = {
#             'trajectory_shape': 'line',
#             'radius': 50,
#             'center': [500, 500],
#             'speed': 100,
#         }
#         fireball_1 = fireball_default.copy()
#         fireball_1['position'] = [400, 500, math.pi / 2]
#         fireball_1['trajectory'] = {
#             'trajectory_shape': 'line',
#             'radius': 60,
#             'center': [400, 100],
#             'angle': math.pi / 2,
#             'speed': 100,
#         }
#         fairy_1 = fairy_default.copy()
#         fairy_1['position'] = [400, 500, math.pi / 2]
#         fairy_1['trajectory'] = {
#             'trajectory_shape': 'pentagon',
#             'radius': 30,
#             'center': [400, 200],
#             'speed': 200,
#         }
#
#         for ent in [basic_1, basic_2, basic_3, absorbable_1, absorbable_2, edible_1, yielder_1,
#                          end_zone, healing_zone, damaging_zone, contact_endzone,
#                          button_door_1, button_door_2, lock_key_door,
#                          moving_1, fireball_1, fairy_1]:
#
#             self.add_entity(ent)
#
#
#         self.starting_ {
#             'type': 'rectangle',
#             'x_range': [50, 150],
#             'y_range': [50, 150],
#             'angle_range': [0, 3.14 * 2],
#         }

