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
        end_zone['position'] = [self.width - 25, self.length - 25, 0]
        end_zone['physical_shape'] = 'rectangle'
        end_zone['shape_rectangle'] = [50, 50]

        self.add_entity(end_zone)
