from ..register import PlaygroundGenerator
from .basic_empty import BasicEmptyPlayground

from ... import scenes as  scenes


@PlaygroundGenerator.register_subclass('rooms_2_edible')
class TwoRoomsEdiblePlayground(BasicEmptyPlayground):

    def __init__(self, params):


        super(TwoRoomsEdiblePlayground, self).__init__(params)


        edible = {
            'physical_shape': 'circle',
            'radius': 20,
            'position': [200, 300, 0],
            'default_color': (0, 250, 100),
            'movable': True,

            'entity_type': 'actionable',
            'actionable_type': 'edible',
            'action_radius': 10,
            'shrink_when_eaten': 0.9,
            'mass': 10,
            'initial_reward': 30
        }
        self.addEntity(edible)


    def generateScene(self, scene_params):

        return scenes.SceneGenerator.create( 'rooms_2' , scene_params)


