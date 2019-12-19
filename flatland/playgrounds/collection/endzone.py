from flatland.playgrounds.playground import PlaygroundGenerator, Playground
from ...default_parameters.entities import *
import random

@PlaygroundGenerator.register_subclass('room_endzone')
class RoomEndZone(Playground):

    def __init__(self, params):

        scenes_params = {
            'scene': {
            'scene_type': 'room',
            'scene_shape': [200, 200]
             },
        }

        death_zone_texture = {
            'type': 'centered_random_tiles',
            'min': [ 150, 0 ,0],
            'max':  [250, 0, 0],
            'size_tiles': 3
        }
        params = { **scenes_params, **params}

        super(RoomEndZone, self).__init__(params)

        end_zone = end_zone_default.copy()
        end_zone['position'] = [self.length - 20, self.width - 20, 0]
        end_zone['physical_shape'] = 'rectangle'
        end_zone['shape_rectangle'] = [20, 20]
        end_zone['reward'] =  50
        self.add_entity(end_zone)

        death_zone_1 = end_zone.copy()
        death_zone_1['position'] = [ 20, self.width - 20, 0]
        death_zone_1['reward'] = -20
        death_zone_1['texture'] = death_zone_texture.copy()
        self.add_entity(death_zone_1)

        death_zone_2 = death_zone_1.copy()
        death_zone_2['position'] = [20, 20, 0]
        self.add_entity(death_zone_2)

        death_zone_3 = death_zone_1.copy()
        death_zone_3['position'] = [self.length - 20, 20, 0]
        self.add_entity(death_zone_3)

        ### Basic entities
        basic_1 = basic_default.copy()
        basic_1['position'] = [140, 150, math.pi / 4]
        basic_1['physical_shape'] = 'rectangle'
        basic_1['movable'] = False
        basic_1['shape_rectangle'] = [10, 20]
        basic_1['texture'] = {
            'type': 'random_tiles',
            'min': [0, 80, 75],
            'max': [0, 100, 100],
            'size_tiles': 4
        }
        self.add_entity(basic_1)


        basic_2 = basic_default.copy()
        basic_2['position'] = [50, 70, math.pi / 2]
        basic_2['physical_shape'] = 'circle'
        basic_2['movable'] = False
        basic_2['radius'] = 10
        basic_2['texture'] = {
            'type': 'centered_random_tiles',
            'radius': 30,
            'min': [0, 50, 150],
            'max': [0, 100, 190],
            'size_tiles': 5
        }

        self.add_entity(basic_2)

        basic_3 = basic_default.copy()
        basic_3['position'] = [140, 60, math.pi / 2]
        basic_3['physical_shape'] = 'pentagon'
        basic_3['movable'] = False
        basic_3['radius'] = 15
        basic_3['texture'] = {
            'type': 'centered_random_tiles',
            'radius': 30,
            'min': [0, 150, 150],
            'max': [50, 200, 190],
            'size_tiles': 5
        }
        self.add_entity(basic_3)

        self.starting_position = {
            'type': 'rectangle',
            'x_range' : [50, 150],
            'y_range' : [50, 150],
            'angle_range' : [0, 3.14*2],
            }

@PlaygroundGenerator.register_subclass('room_contact_endzone')
class RoomContactEndZone(Playground):

    def __init__(self, params):

        scenes_params = {
            'scene': {
            'scene_type': 'room',
            'scene_shape': [200, 200]
             },
        }

        death_zone_texture = {
            'type': 'centered_random_tiles',
            'min': [ 150, 0 ,0],
            'max':  [250, 0, 0],
            'size_tiles': 3
        }
        params = { **scenes_params, **params}

        super(RoomContactEndZone, self).__init__(params)

        end_zone = contact_endzone_default.copy()
        end_zone['position'] = [self.length - 20, self.width - 20, 0]
        end_zone['physical_shape'] = 'rectangle'
        end_zone['shape_rectangle'] = [20, 20]
        end_zone['reward'] =  50
        self.add_entity(end_zone)

        death_zone_1 = end_zone.copy()
        death_zone_1['position'] = [ 20, self.width - 20, 0]
        death_zone_1['reward'] = -20
        death_zone_1['texture'] = death_zone_texture.copy()
        self.add_entity(death_zone_1)

        death_zone_2 = death_zone_1.copy()
        death_zone_2['position'] = [20, 20, 0]
        self.add_entity(death_zone_2)

        death_zone_3 = death_zone_1.copy()
        death_zone_3['position'] = [self.length - 20, 20, 0]
        self.add_entity(death_zone_3)

        ### Basic entities
        basic_1 = basic_default.copy()
        basic_1['position'] = [150, 100, math.pi / 4]
        basic_1['physical_shape'] = 'rectangle'
        basic_1['movable'] = False
        basic_1['shape_rectangle'] = [10, 20]
        basic_1['texture'] = {
            'type': 'random_tiles',
            'min': [0, 80, 75],
            'max': [0, 100, 100],
            'size_tiles': 4
        }
        self.add_entity(basic_1)


        basic_2 = basic_default.copy()
        basic_2['position'] = [50, 100, math.pi / 2]
        basic_2['physical_shape'] = 'circle'
        basic_2['movable'] = False
        basic_2['radius'] = 10
        basic_2['texture'] = {
            'type': 'centered_random_tiles',
            'radius': 30,
            'min': [0, 50, 150],
            'max': [0, 100, 190],
            'size_tiles': 5
        }

        self.add_entity(basic_2)

        self.starting_position = {
            'type': 'rectangle',
            'x_range' : [50, 150],
            'y_range' : [50, 150],
            'angle_range' : [0, 3.14*2],
            }

@PlaygroundGenerator.register_subclass('no_touching')
class NoTouching(Playground):

    def __init__(self, params):

        scenes_params = {
            'scene': {
            'scene_type': 'room',
            'scene_shape': [200, 200]
             },
        }


        params = { **scenes_params, **params}

        super(NoTouching, self).__init__(params)

        basic_1 = contact_endzone_default.copy()
        basic_1['position'] = [random.randint(20, 180),random.randint(20, 180), random.uniform(0, 3.14*2)]
        basic_1['physical_shape'] = 'rectangle'
        basic_1['shape_rectangle'] = [20, 20]
        basic_1['reward'] =  50
        basic_1['texture'] = {
            'type': 'random_tiles',
            'min': [200, 0, 0],
            'max': [250, 0, 0],
            'size_tiles': 3
        }
        self.add_entity(basic_1)

        basic_2 = contact_endzone_default.copy()
        basic_2['position'] = [random.randint(20, 180), random.randint(20, 180), random.uniform(0, 3.14 * 2)]
        basic_2['physical_shape'] = 'pentagon'
        basic_2['shape_rectangle'] = [20, 20]
        basic_2['reward'] = -20
        basic_2['texture'] = {
            'type': 'random_tiles',
            'min': [220, 0, 120],
            'max': [250, 0, 150],
            'size_tiles': 3
        }
        self.add_entity(basic_2)

        basic_3 = contact_endzone_default.copy()
        basic_3['position'] = [random.randint(20, 180), random.randint(20, 180), random.uniform(0, 3.14 * 2)]
        basic_3['physical_shape'] = 'hexagon'
        basic_3['shape_rectangle'] = [20, 20]
        basic_3['reward'] = -20
        basic_3['texture'] = {
            'type': 'random_tiles',
            'min': [0, 200,  150],
            'max': [0, 220,  180],
            'size_tiles': 3
        }
        self.add_entity(basic_3)

        basic_4 = contact_endzone_default.copy()
        basic_4['position'] = [random.randint(20, 180), random.randint(20, 180), random.uniform(0, 3.14 * 2)]
        basic_4['physical_shape'] = 'hexagon'
        basic_4['shape_rectangle'] = [20, 20]
        basic_4['reward'] = -20
        basic_4['texture'] = {
            'type': 'random_tiles',
            'min': [0, 0, 50],
            'max': [0, 20, 80],
            'size_tiles': 3
        }
        self.add_entity(basic_4)

        self.starting_position = {
            'type': 'rectangle',
            'x_range' : [50, 150],
            'y_range' : [50, 150],
            'angle_range' : [0, 3.14*2],
            }
