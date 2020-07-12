from flatland.entities.scene_elements.element import SceneElement


class Basic(SceneElement):

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


class Door(SceneElement):

    entity_type = 'door'

    def __init__(self, initial_position, **kwargs):
        """ Door that can be opened with a switch

        Default: Pale green door

        Args:
            initial_position: initial position of the entity. can be list [x,y,theta], AreaPositionSampler or Trajectory
            **kwargs: other params to configure entity. Refer to Entity class
        """

        default_config = self._parse_configuration('interactive', 'door')
        entity_params = {**default_config, **kwargs}

        super(Door, self).__init__(initial_position=initial_position, **entity_params)

        self.opened = False

    def open_door(self):

        self.opened = True
        # self.visible = False

    def close_door(self):
        self.opened = False
        # self.visible = True

    def reset(self):

        self.close_door()
        super().reset()

