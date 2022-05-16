from _pytest.mark import param
import pytest
from copy import Error
import gc

from simple_playgrounds.playground.playground import EmptyPlayground
from tests.mock_entities import MockPhysicalMovable, MockZoneInteractive, MockPhysicalInteractive, MockHalo
from simple_playgrounds.entity.embodied.physical import PhysicalEntity

coord_center = (0, 0), 0

def test_playground_interface_basic_element():

    playground = EmptyPlayground()

    assert not playground._entities

    ent_1 = MockPhysicalMovable(playground, coord_center)
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

    ent_1 = MockZoneInteractive(playground, coord_center, 35, 10)
 
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

    ent_1 = MockPhysicalInteractive(playground, coord_center, radius = 20, interaction_range=10, triggered = True)
 

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
 
    MockPhysicalMovable(playground, coord_center)

    del playground
    gc.collect()
    for obj in gc.get_objects():
        if isinstance(obj, EmptyPlayground):
            raise Error
        if isinstance(obj, MockPhysicalMovable):
            raise Error

def test_gc_remove_physical():

    playground = EmptyPlayground()
    MockPhysicalMovable(playground, coord_center)
 
    gc.collect()
    in_gc = len([obj for obj in gc.get_objects() if isinstance(obj, MockPhysicalMovable)])
    assert in_gc

    playground._entities[0].remove(definitive=False)

    gc.collect()
    in_gc = len([obj for obj in gc.get_objects() if isinstance(obj, MockPhysicalMovable)])
    assert in_gc

    playground.reset()
    
    playground._entities[0].remove(definitive=True)
    gc.collect()
    in_gc = len([obj for obj in gc.get_objects() if isinstance(obj, MockPhysicalMovable)])
    assert not in_gc


def test_gc_remove_anchored():

    playground = EmptyPlayground()
 
    MockPhysicalInteractive(playground, coord_center, radius = 20, interaction_range=10, triggered = True)
    
    gc.collect()
    in_gc = len([obj for obj in gc.get_objects() if isinstance(obj, MockPhysicalInteractive) or isinstance(obj, PhysicalEntity) or isinstance(obj, MockHalo)])
    assert in_gc

    playground._entities[0].remove(definitive=False)

    gc.collect()
    in_gc = len([obj for obj in gc.get_objects() if isinstance(obj, MockPhysicalInteractive) or isinstance(obj, PhysicalEntity) or isinstance(obj, MockHalo)])
    assert in_gc

    playground.reset()
    
    playground._entities[0].remove(definitive=True)
    gc.collect()
    in_gc = len([obj for obj in gc.get_objects() if isinstance(obj, MockPhysicalInteractive) or isinstance(obj, PhysicalEntity) or isinstance(obj, MockHalo)])
    assert not in_gc
