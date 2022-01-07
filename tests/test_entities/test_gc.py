from copy import Error
import gc

from simple_playgrounds.playground.playground import EmptyPlayground
from tests.mock_entities import MockPhysical, MockHaloTrigger, MockZoneTriggered
from simple_playgrounds.entity.embodied.contour import Contour



class GCPlayground(EmptyPlayground):

    def __init__(self):
        super().__init__()

        contour = Contour(shape='circle', radius=5)
        MockPhysical(playground=self, **contour.dict_attributes, 
                         movable=True, mass=5,
                         initial_coordinates=((0, 0), 0))
    

def test_gc_del():

    playground = GCPlayground()

    assert playground.physical_entities

    del playground
    gc.collect()
    for obj in gc.get_objects():
        if isinstance(obj, EmptyPlayground):
            raise Error
        if isinstance(obj, MockPhysical):
            raise Error

def test_gc_remove_entity():

    playground = GCPlayground()
    contour = Contour(shape='circle', radius=5)
    ent_1 = MockPhysical(playground=playground, **contour.dict_attributes, 
                         movable=True, mass=5,
                         initial_coordinates=((0, 0), 0))
   
    assert ent_1 in playground.physical_entities
    playground.remove(ent_1, definitive=True)

    assert playground.physical_entities

    gc.collect()
    for obj in gc.get_objects():
        if obj is ent_1: raise Error
