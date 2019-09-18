import pymunk, random, pygame

from .basic import  Basic
from .entity import Entity
from flatland.utils.config import *


class Activable(Basic):

    def __init__(self, params ):
        """
        Instantiate an obstacle with the following parameters
        :param pos: 2d tuple or 'random', position of the fruit
        :param environment: the environment calling the creation of the fruit
        """
        params['visible'] = True
        params['interactive'] = True

        super(Activable, self).__init__(params)

        self.params = params


class ActivableGenerator():

    subclasses = {}

    @classmethod
    def register_subclass(cls, activable_type):
        def decorator(subclass):
            cls.subclasses[activable_type] = subclass
            return subclass

        return decorator

    @classmethod
    def create(cls, params):
        activable_type = params['activable_type']
        if activable_type not in cls.subclasses:
            raise ValueError('Entity type not implemented:' + activable_type)

        return cls.subclasses[activable_type](params)



@ActivableGenerator.register_subclass('distractor')
class DistractorObject(Activable):

    def __init__(self, params):

        super(DistractorObject, self).__init__(params)

        self.pm_sensor.collision_type = collision_types['activable']


    def actionate(self):

        self.pm_shape.color = (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))




#        self.__init__(self.params)
        #self.initialize_texture()


@ActivableGenerator.register_subclass('dispenser')
class DispenserObject(Activable):

    def __init__(self, params):

        super(DispenserObject, self).__init__(params)

        self.pm_sensor.collision_type = collision_types['activable']

        self.object_produced = params['object_produced']

        self.production_area_shape = params['area_shape']
        self.production_area = params['area']

        self.limit = params['limit']

        self.produced_elements = []


    def actionate(self):

        obj = self.object_produced

        if self.production_area_shape == 'rectangle':

            x = random.uniform( self.production_area[0][0],self.production_area[1][0] )
            y = random.uniform( self.production_area[0][1],self.production_area[1][1] )

            obj['position'] = (x,y,0)

        return obj

@ActivableGenerator.register_subclass('graspable')
class GraspableObject(Activable):

    def __init__(self, params):

        super(GraspableObject, self).__init__( params)

        self.pm_sensor.collision_type = collision_types['graspable']

        self.graspable = True

    def actionate(self):
        pass



@ActivableGenerator.register_subclass('door_opener')
class DoorObject(Activable):

    def __init__(self, params):

        super(DoorObject, self).__init__(params)

        self.pm_sensor.collision_type = collision_types['activable']

        self.door_params = params['door']

        self.time_open = params['time_open']

        self.door_opened = False

    def assign_door(self, door):

        self.door = door

    def start_timer(self):

        self.timer = self.time_open

    def update_timer(self):

        self.timer -= 1



