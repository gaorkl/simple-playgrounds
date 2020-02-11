from flatland.playgrounds.playground import PlaygroundGenerator, Playground
from flatland.default_parameters.entities import *


@PlaygroundGenerator.register_subclass('chest-test')
class ChestTest(Playground):

    def __init__(self, params):
        scenes_params = {
            'scene': {
                'scene_type': 'room',
                'scene_shape': [200, 200]
            },
        }

        params = {**scenes_params, **params}

        super(ChestTest, self).__init__(params)

        end_zone = end_zone_default.copy()
        end_zone['position'] = [20, self.width - 20, 0]
        end_zone['physical_shape'] = 'rectangle'
        end_zone['shape_rectangle'] = [20, 20]
        end_zone['reward'] = 50
        self.add_entity(end_zone)

        ### Basic entities
        pod = chest_default.copy()
        pod['position'] = [100, 100, math.pi / 4]
        pod['key_pod']['position'] = [30, 30, 0]

        self.add_entity(pod)

        self.starting_position = {
            'type': 'rectangle',
            'x_range': [50, 150],
            'y_range': [50, 150],
            'angle_range': [0, 3.14 * 2],
        }
