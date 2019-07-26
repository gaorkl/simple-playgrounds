from ..register import PlaygroundGenerator
from .basic_empty import BasicEmptyPlayground

from ... import scenes as  scenes


@PlaygroundGenerator.register_subclass('rooms_2_empty')
class BasicFieldPlayground(BasicEmptyPlayground):

    def __init__(self, params):

        super(BasicFieldPlayground, self).__init__(params)

    def generateScene(self, scene_params):

        return scenes.SceneGenerator.create( 'rooms_2' , scene_params)


