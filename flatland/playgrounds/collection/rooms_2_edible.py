from ..register import PlaygroundGenerator
from flatland.playgrounds.basic import BasicEmptyPlayground
from ...common.default_entities_parameters import edible_default


@PlaygroundGenerator.register_subclass('rooms_2_edible')
class TwoRoomsEdiblePlayground(BasicEmptyPlayground):

    def __init__(self, params):

        if 'scene' in params:
            params['scene']['scene_type']  = 'rooms_2'

        super(TwoRoomsEdiblePlayground, self).__init__(params)

        y = self.width * 3 / 4.0
        x = self.height / 2.0

        edible = edible_default.copy()
        edible['position'] = [x, y, 0]

        self.add_entity(edible)




