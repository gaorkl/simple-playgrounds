from _pytest.mark import param
import pytest
from copy import Error
import gc

from simple_playgrounds.playground.playground import EmptyPlayground
from tests.mock_entities import MockPhysical, MockHaloTrigger, MockZoneTrigger
from simple_playgrounds.entity.embodied.contour import Contour


def test_playground_interface_basic_element():

    playground = EmptyPlayground()

    assert not playground._entities

    contour = Contour(shape='circle', radius=5)
    ent_1 = MockPhysical(playground, ((0, 0), 0), **contour.dict_attributes)
 
    assert ent_1 in playground.entities

    ent_1.remove()

    assert ent_1 not in playground.entities
    assert ent_1 in playground._entities
    assert ent_1._removed
    
    playground.reset()

    assert ent_1 in playground.entities
    assert not ent_1.removed
    
    ent_1.remove(definitive=True)

    assert ent_1 not in playground.entities
    assert ent_1 not in playground._entities
    assert ent_1._removed
   
    playground.reset()

    assert ent_1 not in playground.entities
    assert ent_1 not in playground._entities
    assert ent_1._removed

    assert not playground.space.shapes
    assert not playground.space.bodies



def test_playground_interface_interactive_element():

    playground = EmptyPlayground()

    assert not playground._entities

    contour = Contour(shape='circle', radius=5)
    ent_1 = MockZoneTrigger(playground, ((0, 0), 0), **contour.dict_attributes)
 
    assert ent_1 in playground.entities

    ent_1.remove()

    assert ent_1 not in playground.entities
    assert ent_1 in playground._entities
    assert ent_1._removed
    
    playground.reset()

    assert ent_1 in playground.entities
    assert not ent_1.removed
    
    ent_1.remove(definitive=True)

    assert ent_1 not in playground.entities
    assert ent_1 not in playground._entities
    assert ent_1._removed
   
    playground.reset()

    assert ent_1 not in playground.entities
    assert ent_1 not in playground._entities
    assert ent_1._removed

    assert not playground.space.shapes
    assert not playground.space.bodies


def test_playground_interface_anchored_interactive_element():

    playground = EmptyPlayground()

    assert not playground._entities

    contour = Contour(shape='circle', radius=5)
    ent_1 = MockPhysical(playground, ((0, 0), 0), **contour.dict_attributes)
 
    MockHaloTrigger(ent_1, **contour.dict_attributes)

    assert ent_1 in playground.entities

    ent_1.remove()

    assert ent_1 not in playground.entities
    assert ent_1 in playground._entities
    assert ent_1._removed
    
    playground.reset()

    assert ent_1 in playground.entities
    assert not ent_1.removed
    
    ent_1.remove(definitive=True)

    assert ent_1 not in playground.entities
    assert ent_1 not in playground._entities
    assert ent_1._removed
   
    playground.reset()

    assert ent_1 not in playground.entities
    assert ent_1 not in playground._entities
    assert ent_1._removed

    assert not playground.space.shapes
    assert not playground.space.bodies



def test_gc_del():

    playground = EmptyPlayground()
    contour = Contour(shape='circle', radius=5)
    MockPhysical(playground, ((0, 0), 0), **contour.dict_attributes)
 
    del playground
    gc.collect()
    for obj in gc.get_objects():
        if isinstance(obj, EmptyPlayground):
            raise Error
        if isinstance(obj, MockPhysical):
            raise Error

def test_gc_remove_physical():

    playground = EmptyPlayground()
    contour = Contour(shape='circle', radius=5)
    MockPhysical(playground, ((0, 0), 0), **contour.dict_attributes)
 
    gc.collect()
    in_gc = len([obj for obj in gc.get_objects() if isinstance(obj, MockPhysical)])
    assert in_gc

    playground._entities[0].remove(definitive=False)

    gc.collect()
    in_gc = len([obj for obj in gc.get_objects() if isinstance(obj, MockPhysical)])
    assert in_gc

    playground.reset()
    
    playground._entities[0].remove(definitive=True)
    gc.collect()
    in_gc = len([obj for obj in gc.get_objects() if isinstance(obj, MockPhysical)])
    assert not in_gc


def test_gc_remove_anchored():

    playground = EmptyPlayground()
    contour = Contour(shape='circle', radius=5)
    MockHaloTrigger(MockPhysical(playground, ((0, 0), 0), **contour.dict_attributes))
 
    gc.collect()
    in_gc = len([obj for obj in gc.get_objects() if isinstance(obj, MockPhysical) or isinstance(obj, MockHaloTrigger)])
    assert in_gc

    playground._entities[0].remove(definitive=False)

    gc.collect()
    in_gc = len([obj for obj in gc.get_objects() if isinstance(obj, MockPhysical) or isinstance(obj, MockHaloTrigger)])
    assert in_gc

    playground.reset()
    
    playground._entities[0].remove(definitive=True)
    gc.collect()
    in_gc = len([obj for obj in gc.get_objects() if isinstance(obj, MockPhysical) or isinstance(obj, MockHaloTrigger)])
    assert not in_gc
