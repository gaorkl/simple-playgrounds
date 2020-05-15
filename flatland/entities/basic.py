from flatland.entities.entity import Entity


class Basic(Entity):

    visible = True
    entity_type = 'basic'

    def __init__(self, initial_position, default_config_key = None, **kwargs):
        '''

        :param position: initial position of the entity. can be list [x,y,theta] or position sampler
        :param default_config_key: default configurations. Can be circle, square, rectangle, pentagon, hexagon
        :param kwargs: other params to configure entity
        '''

        default_config = self.parse_configuration('basic', default_config_key)
        entity_params = {**default_config, **kwargs}

        super(Basic, self).__init__(initial_position = initial_position, **entity_params)
