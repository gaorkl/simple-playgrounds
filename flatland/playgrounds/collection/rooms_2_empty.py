from ..playground import PlaygroundGenerator
from flatland.playgrounds.playground import Playground

from ..scene_layout import SceneGenerator


@PlaygroundGenerator.register_subclass('rooms_2_empty')
class BasicFieldPlayground(Playground):

    def __init__(self, params):

        super(BasicFieldPlayground, self).__init__(params)

    def generate_scene(self, scene_params):

        return SceneGenerator.create( scene_params)


