from ..playground import PlaygroundGenerator
from flatland.playgrounds.playground import Playground

@PlaygroundGenerator.register_subclass('basic_field')
class BasicFieldPlayground(Playground):

    def __init__(self, scene = None):

        super(BasicFieldPlayground, self).__init__(scene)

        pellet = {
            'physical_shape': 'circle',
            'radius': 5,
            'default_color': (0, 250, 0),
            'absorbable': True,
            'movable': True,
            'mass': 5,
            'reward': 5
        }

        yielder = {
            'entity_type': 'yielder',

            'object': pellet,
            'area_shape': 'rectangle',
            'area': ((50, 50), (70, 70)),
            'probability': 1.0 / 60,
            'limit': 5
        }

        self.add_entity(yielder)

