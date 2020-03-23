from flatland.playgrounds.playground import PlaygroundGenerator, Playground

death_zone_texture = {
            'type': 'centered_random_tiles',
            'min': [ 150, 0 ,0],
            'max':  [250, 0, 0],
            'size_tiles': 3
        }

end_zone = end_zone_default.copy()
end_zone['physical_shape'] = 'rectangle'
end_zone['shape_rectangle'] = [20, 20]
end_zone['reward'] =  50

death_zone_1 = end_zone.copy()
death_zone_1['physical_shape'] = 'rectangle'
death_zone_1['reward'] = -20
death_zone_1['texture'] = death_zone_texture.copy()


@PlaygroundGenerator.register_subclass('fixed_objects_visible_endzone')
class Endzone_1(Playground):

    def __init__(self, params):

        scenes_params = {
            'scene': {
            'scene_type': 'room',
            'scene_shape': [200, 200]
             },
        }
        
        params = { **scenes_params, **params}
        super(Endzone_1, self).__init__(params)

        end_zone = end_zone_default.copy()
        end_zone['position'] = [self.length - 20, self.width - 20, 0]
        end_zone['physical_shape'] = 'rectangle'
        end_zone['shape_rectangle'] = [20, 20]
        end_zone['reward'] =  50
        self.add_entity(end_zone)

        
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
            'radius': 20,
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
            'radius': 25,
            'min': [0, 150, 150],
            'max': [50, 200, 190],
            'size_tiles': 5
        }
        self.add_entity(basic_3)

        basic_4 = basic_default.copy()
        basic_4['position'] = [60, 120, math.pi / 2]
        basic_4['physical_shape'] = 'pentagon'
        basic_4['movable'] = False
        basic_4['radius'] = 15
        basic_4['texture'] = {
            'type': 'centered_random_tiles',
            'radius': 30,
            'min': [150, 150, 150],
            'max': [160, 200, 190],
            'size_tiles': 5
        }
        self.add_entity(basic_4)

        self.starting_position = {
            'type': 'rectangle',
            'x_range' : [50, 150],
            'y_range' : [50, 150],
            'angle_range' : [0, 3.14*2],
            }

        
@PlaygroundGenerator.register_subclass('baseline_2')
class Baseline_2(Playground):

    def __init__(self, params):

        scenes_params = {
            'scene': {
            'scene_type': 'room',
            'scene_shape': [200, 200]
             },
        }
        
        params = { **scenes_params, **params}

        super(Baseline_2, self).__init__(params)

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
        basic_1['position'] = [130, 120, 2*math.pi / 7]
        basic_1['physical_shape'] = 'rectangle'
        basic_1['movable'] = False
        basic_1['shape_rectangle'] = [10, 20]
        basic_1['texture'] = {
            'type': 'random_tiles',
            'min': [50, 180, 75],
            'max': [70, 200, 100],
            'size_tiles': 4
        }
        self.add_entity(basic_1)


        basic_2 = basic_default.copy()
        basic_2['position'] = [50, 80, math.pi / 2]
        basic_2['physical_shape'] = 'circle'
        basic_2['movable'] = False
        basic_2['radius'] = 10
        basic_2['texture'] = {
            'type': 'centered_random_tiles',
            'radius': 20,
            'min': [ 180, 0, 150],
            'max': [ 200, 0, 190],
            'size_tiles': 10
        }

        self.add_entity(basic_2)

        basic_3 = basic_default.copy()
        basic_3['position'] = [130, 50, math.pi / 2]
        basic_3['physical_shape'] = 'pentagon'
        basic_3['movable'] = False
        basic_3['radius'] = 15
        basic_3['texture'] = {
            'type': 'centered_random_tiles',
            'radius': 25,
            'min': [0, 0, 150],
            'max': [50, 0, 200],
            'size_tiles': 5
        }
        self.add_entity(basic_3)

        basic_4 = basic_default.copy()
        basic_4['position'] = [60, 150, math.pi /3]
        basic_4['physical_shape'] = 'triangle'
        basic_4['movable'] = False
        basic_4['radius'] = 15
        basic_4['texture'] = {
            'type': 'centered_random_tiles',
            'radius': 30,
            'min': [150, 150, 150],
            'max': [160, 200, 190],
            'size_tiles': 5
        }
        self.add_entity(basic_4)

        self.starting_position = {
            'type': 'rectangle',
            'x_range' : [50, 150],
            'y_range' : [50, 150],
            'angle_range' : [0, 3.14*2],
            }


@PlaygroundGenerator.register_subclass('baseline_3')
class Baseline_3(Playground):

    def __init__(self, params):

        scenes_params = {
            'scene': {
            'scene_type': 'room',
            'scene_shape': [200, 200]
             },
        }
        
        params = { **scenes_params, **params}

        super(Baseline_3, self).__init__(params)

        end_zone = contact_endzone_default.copy()
        end_zone['position'] = [self.length - 20, self.width - 20, 0]
        end_zone['physical_shape'] = 'rectangle'
        end_zone['shape_rectangle'] = [20, 20]
        end_zone['reward'] =  50
        self.add_entity(end_zone)

        
        ### Basic entities
        basic_1 = basic_default.copy()
        basic_1['position'] = [130, 150, math.pi / 4]
        basic_1['physical_shape'] = 'rectangle'
        basic_1['movable'] = False
        basic_1['shape_rectangle'] = [15, 20]
        basic_1['texture'] = {
            'type': 'random_tiles',
            'min': [200, 80, 75],
            'max': [220, 100, 100],
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
            'radius': 20,
            'min': [0, 50, 150],
            'max': [0, 100, 190],
            'size_tiles': 5
        }

        self.add_entity(basic_2)

        basic_3 = basic_default.copy()
        basic_3['position'] = [150, 55, math.pi / 2]
        basic_3['physical_shape'] = 'pentagon'
        basic_3['movable'] = False
        basic_3['radius'] = 15
        basic_3['texture'] = {
            'type': 'centered_random_tiles',
            'radius': 25,
            'min': [0, 150, 150],
            'max': [50, 200, 190],
            'size_tiles': 5
        }
        self.add_entity(basic_3)

        basic_4 = basic_default.copy()
        basic_4['position'] = [60, 135, math.pi / 2]
        basic_4['physical_shape'] = 'hexagon'
        basic_4['movable'] = False
        basic_4['radius'] = 15
        basic_4['texture'] = {
            'type': 'centered_random_tiles',
            'radius': 30,
            'min': [150, 150, 150],
            'max': [160, 200, 190],
            'size_tiles': 5
        }
        self.add_entity(basic_4)

        self.starting_position = {
            'type': 'rectangle',
            'x_range' : [50, 150],
            'y_range' : [50, 150],
            'angle_range' : [0, 3.14*2],
            }

        
@PlaygroundGenerator.register_subclass('baseline_4')
class Baseline_4(Playground):

    def __init__(self, params):

        scenes_params = {
            'scene': {
            'scene_type': 'room',
            'scene_shape': [200, 200]
             },
        }
        
        params = { **scenes_params, **params}

        super(Baseline_4, self).__init__(params)

        end_zone = contact_endzone_default.copy()
        end_zone['position'] = [self.length - 20, self.width - 20, 0]
        end_zone['physical_shape'] = 'rectangle'
        end_zone['shape_rectangle'] = [20, 20]
        end_zone['reward'] =  50
        self.add_entity(end_zone)

        death_zone_1 = contact_endzone_default.copy()
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
        basic_1['position'] = [60, 150, math.pi / 4]
        basic_1['physical_shape'] = 'rectangle'
        basic_1['movable'] = False
        basic_1['shape_rectangle'] = [15, 20]
        basic_1['texture'] = {
            'type': 'random_tiles',
            'min': [200, 80, 0],
            'max': [220, 100, 50],
            'size_tiles': 4
        }
        self.add_entity(basic_1)


        basic_2 = basic_default.copy()
        basic_2['position'] = [150, 70, math.pi / 2]
        basic_2['physical_shape'] = 'square'
        basic_2['movable'] = False
        basic_2['radius'] = 10
        basic_2['texture'] = {
            'type': 'centered_random_tiles',
            'radius': 20,
            'min': [0, 0, 150],
            'max': [0, 50, 190],
            'size_tiles': 5
        }

        self.add_entity(basic_2)

        basic_3 = basic_default.copy()
        basic_3['position'] = [50, 55, math.pi / 2]
        basic_3['physical_shape'] = 'pentagon'
        basic_3['movable'] = False
        basic_3['radius'] = 15
        basic_3['texture'] = {
            'type': 'centered_random_tiles',
            'radius': 25,
            'min': [100, 50, 150],
            'max': [150, 100, 190],
            'size_tiles': 5
        }
        self.add_entity(basic_3)

        basic_4 = basic_default.copy()
        basic_4['position'] = [150, 135, math.pi / 2]
        basic_4['physical_shape'] = 'circle'
        basic_4['movable'] = False
        basic_4['radius'] = 15
        basic_4['texture'] = {
            'type': 'centered_random_tiles',
            'radius': 30,
            'min': [150, 150, 150],
            'max': [160, 200, 190],
            'size_tiles': 5
        }
        self.add_entity(basic_4)

        self.starting_position = {
            'type': 'rectangle',
            'x_range' : [50, 150],
            'y_range' : [50, 150],
            'angle_range' : [0, 3.14*2],
            }

