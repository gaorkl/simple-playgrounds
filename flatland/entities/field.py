import random, os, yaml
# from .entity import EntityGenerator


# @EntityGenerator.register('field')
class Field:

    id_number = 0
    entity_type = 'field'

    def __init__(self, entity_produced, entity_produced_params=None, production_area=None, **kwargs):
        """

        Args:
            entity_produced: Class of the entity produced by the field
            entity_produced_params: Dictionary of additional parameters for the entity_produced
            production_area: PositionAreaSampler
            **kwargs: Additional Keywork arguments

        Keyword Args:
            total_produced_limit: total number of entities that a field can produce during an episode. Default: 30
            current_produced_limit: total number of entities produced currently on the playground. Default: 30 10
            production_probability : probability of producing an entity at each timestep. Default: 0.1

        """
        fname = 'configs/field_default.yml'

        __location__ = os.path.realpath(os.path.join(os.getcwd(), os.path.dirname(__file__)))
        with open(os.path.join(__location__, fname), 'r') as yaml_file:
            default_config = yaml.load(yaml_file)

        entity_params = {**default_config['field'], **kwargs}

        self.entity_produced = entity_produced
        self.location_sampler = production_area

        if entity_produced_params is None:
            self.entity_produced_params = {}
        else:
            self.entity_produced_params = entity_produced_params

        self.probability = entity_params.get('production_probability')
        self.limit = entity_params.get('current_produced_limit')

        self.total_limit = entity_params.get('total_produced_limit')
        self.total_produced = 0
        self.produced_entities = []

        # Internal counter to assign identity number to each entity
        self.name = 'field_' + str(Field.id_number)
        Field.id_number += 1

    def can_produce(self):

        if len(self.produced_entities) < self.limit \
                and self.total_produced < self.total_limit\
                and random.random() < self.probability:
            return True

        else:
            return False

    def produce(self):

        obj = self.entity_produced(initial_position=self.location_sampler, **self.entity_produced_params)
        obj.is_temporary_entity = True

        self.total_produced += 1
        self.produced_entities.append(obj)

        return obj

    def reset(self):

        self.produced_entities = []
        self.total_produced = 0
