from ..playground import PlaygroundGenerator
from flatland.playgrounds.playground import Playground
from ...default_parameters.entities import edible_default


@PlaygroundGenerator.register_subclass('rooms_2_edible')
class TwoRoomsEdiblePlayground(Playground):

    def __init__(self, params):

        if 'scene' in params:
            params['scene']['scene_type']  = 'rooms_2'

        super(TwoRoomsEdiblePlayground, self).__init__(params)

        y = self.width * 3 / 4.0
        x = self.length / 2.0

        edible = edible_default.copy()
        edible['position'] = [x, y, 0]

        self.add_entity(edible)




