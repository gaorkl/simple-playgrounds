from simple_playgrounds.playground import PlaygroundRegister
from simple_playgrounds.playgrounds.empty import SingleRoom
from simple_playgrounds.playgrounds.scene_elements import *


@PlaygroundRegister.register('test_test', 'basic')
class Basics(SingleRoom):

    def __init__(self):

        super().__init__(size=(200, 200))

        texture_obj = {'texture_type': 'color',
                       'color': [100, 220, 170]}

        obj_params = { 'texture': texture_obj,
                       'physical_shape': 'square',
                       'radius': 22
                       }

        self.my_obj = Basic([150, 160, 0.2], **obj_params)

        self.add_scene_element(self.my_obj)


def test_new_object():

    pg = PlaygroundRegister.playgrounds['test_test']['basic']()
    assert pg.my_obj.radius == 22