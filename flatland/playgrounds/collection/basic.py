from flatland.playgrounds.playground import PlaygroundGenerator, Playground
from ...default_parameters.entities import *


@PlaygroundGenerator.register_subclass('basic_empty')
class BasicEmpty(Playground):

    def __init__(self, params):

        super(BasicEmpty, self).__init__(params)


@PlaygroundGenerator.register_subclass('basic_endzone')
class BasicEndZone(Playground):

    def __init__(self, params):

        super(BasicEndZone, self).__init__(params)

        end_zone = end_zone_default.copy()
        end_zone['position'] = [self.length - 25, self.width - 25, 0]
        end_zone['physical_shape'] = 'rectangle'
        end_zone['shape_rectangle'] = [50, 50]

        self.add_entity(end_zone)

@PlaygroundGenerator.register_subclass('basic_endzone_contact_fireball')
class BasicEndZoneContactFireball(Playground):

    def __init__(self, params):

        super(BasicEndZoneContactFireball, self).__init__(params)

        contact_endzone = contact_endzone_default.copy()
        contact_endzone['position'] =  [self.length - 25, self.width - 25, 0]

        self.add_entity(contact_endzone)

        fireball = fireball_default.copy()
        fireball['position'] = [self.width / 2, self.length / 2, math.pi / 2]
        fireball['trajectory'] = {
            'trajectory_shape': 'line',
            'radius': self.width / 2,
            'center': [self.length / 2, self.width / 2],
            'angle': math.pi / 2,
            'speed': 60,
        }

        self.add_entity(fireball)