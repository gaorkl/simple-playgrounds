from ..register import PlaygroundGenerator
from flatland.playgrounds.playground import Playground

from ... import scenes as  scenes


@PlaygroundGenerator.register_subclass('rooms_2_empty')
class BasicFieldPlayground(Playground):

    def __init__(self, params):

        super(BasicFieldPlayground, self).__init__(params)

    def generate_scene(self, scene_params):

        return scenes.SceneGenerator.create( 'rooms_2' , scene_params)


