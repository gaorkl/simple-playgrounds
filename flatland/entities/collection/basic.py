from flatland.entities.entity import Entity


# @EntityGenerator.register('basic')
class Basic(Entity):

    visible = True
    entity_type = 'basic'

    def __init__(self, initial_position, default_config_key=None, **kwargs):
        """ Base class for Basic entities.

        Basic entities are non-interactive entities.

        Args:
            initial_position: initial position of the entity. can be list [x,y,theta], AreaPositionSampler or Trajectory
            default_config_key: default configurations. Can be circle, square, rectangle, pentagon, hexagon
            **kwargs: other params to configure entity. Refer to Entity class for physical properties

        """

        default_config = self._parse_configuration('basic', default_config_key)
        entity_params = {**default_config, **kwargs}

        super(Basic, self).__init__(initial_position=initial_position, **entity_params)
