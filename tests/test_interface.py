from simple_playgrounds.playgrounds.playground import PlaygroundRegister
from simple_playgrounds.playgrounds.layouts import SingleRoom
from simple_playgrounds.elements.collection.basic import Physical


@PlaygroundRegister.register('test_test', 'basic')
class Basics(SingleRoom):
    def __init__(self):

        super().__init__(size=(200, 200))

        texture_obj = {'texture_type': 'color', 'color': [100, 220, 170]}

        obj_params = {
            'texture': texture_obj,
            'physical_shape': 'square',
            'radius': 22
        }

        self.my_obj = Physical(**obj_params)

        self.add_element(self.my_obj, ((150, 160), 0.2))


def test_new_object():

    pg = Basics()
    assert pg.my_obj.radius == 22


# TODO: add test add element without overlapping
