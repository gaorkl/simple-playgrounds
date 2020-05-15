import random, os, yaml


class Field():

    id_number = 0
    entity_type = 'field'

    def __init__(self, entity_produced, entity_produced_params = None, production_area = None, **kwargs):

        fname = 'configs/field_default.yml'

        __location__ = os.path.realpath(os.path.join(os.getcwd(), os.path.dirname(__file__)))
        with open(os.path.join(__location__, fname), 'r') as yaml_file:
            default_config = yaml.load(yaml_file)

        entity_params = {**default_config['field'], **kwargs}

        self.entity_produced = entity_produced
        self.location_sampler = production_area

        self.probability = entity_params.get('production_probability')
        self.limit = entity_params.get('current_produced_limit')

        self.total_limit = entity_params.get('total_produced_limit')
        self.total_produced = 0
        self.produced_entities = []

        print(self.limit, self.total_limit)

        # # Internal counter to assign identity number to each entity
        # self.name_id = 'yielder_' + str(Yielder.id_number)
        # Yielder.id_number += 1

    def can_produce(self):

        if len(self.produced_entities) < self.limit \
                and self.total_produced < self.total_limit\
                and random.random() < self.probability:
            return True

        else:
            return False


    def produce(self):

        obj = self.entity_produced(initial_position = self.location_sampler)
        obj.is_temporary_entity = True

        self.total_produced += 1
        self.produced_entities.append(obj)

        return obj

    def reset(self):
        self.produced_entities = []
        self.total_produced = 0

