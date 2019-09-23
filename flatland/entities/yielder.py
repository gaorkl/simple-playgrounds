import random
from .entity import EntityGenerator
from ..default_parameters.entities import *

@EntityGenerator.register_subclass('yielder')
class Yielder():

    id_number = 0

    def __init__(self, params ):
        """
        Instantiate an obstacle with the following parameters
        :param pos: 2d tuple or 'random', position of the fruit
        :param environment: the environment calling the creation of the fruit
        """

        params = {**yielder_default, **params}

        self.entity_type = 'yielder'

        self.object_produced = params['object_produced']

        self.production_area_shape = params['area_shape']
        self.production_area = params['area']

        self.probability = params.get('probability', 0.1)

        self.limit = params.get('limit', 4)

        self.yielded_elements = []

        # Internal counter to assign identity number to each entity
        self.name_id = 'yielder_' + str(Yielder.id_number)
        Yielder.id_number += 1


    def produce(self):

        obj = self.object_produced

        if self.production_area_shape == 'rectangle':

            x = random.uniform( self.production_area[0][0],self.production_area[1][0] )
            y = random.uniform( self.production_area[0][1],self.production_area[1][1] )

            obj['position'] = (x,y,0)

        return obj
