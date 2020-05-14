from flatland.entities.entity import Entity, EntityGenerator
import os, yaml
import random

__location__ = os.path.realpath(os.path.join(os.getcwd(), os.path.dirname(__file__)))

with open(os.path.join(__location__, 'configs/yielder_default.yml'), 'r') as yaml_file:
    default_config = yaml.load(yaml_file)

with open(os.path.join(__location__, 'configs/basic_default.yml'), 'r') as yaml_file:
    absorbable_config = yaml.load(yaml_file)['absorbable']


@EntityGenerator.register_subclass('yielder')
class Yielder():

    id_number = 0

    def __init__(self, custom_params ):
        """
        Instantiate an obstacle with the following parameters
        :param pos: 2d tuple or 'random', position of the fruit
        :param environment: the environment calling the creation of the fruit
        """

        self.entity_type = 'yielder'

        params = {**default_config['yielder'], **custom_params}

        self.entity_produced = params.get('entity_produced', absorbable_config)

        self.location_sampler = params.get('area', None)

        self.probability = params.get('production_probability')
        self.limit = params.get('current_produced_limit')
        self.total_limit = params.get('total_produced_limit')

        self.total_produced = 0

        self.produced_entities = []

        # Internal counter to assign identity number to each entity
        self.name_id = 'yielder_' + str(Yielder.id_number)
        Yielder.id_number += 1

    def can_produce(self):

        if len(self.produced_entities) < self.limit \
                and self.total_produced < self.total_limit\
                and random.random() < self.probability:
            return True

        else:
            return False


    def produce(self):

        obj = self.entity_produced
        position = self.location_sampler.sample()
        obj['position'] = position

        self.total_produced += 1

        entity_type = 'absorbable'

        return entity_type, obj

    def reset(self):
        self.produced_entities = []
        self.total_produced = 0

