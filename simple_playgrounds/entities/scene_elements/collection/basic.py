"""
Module for Basic SceneElements
"""
from simple_playgrounds.entities.scene_elements.element import SceneElement


class Basic(SceneElement):
    """ Basic Scene elements are non-interactive obstacles."""
    visible = True
    entity_type = 'basic'

    def __init__(self, initial_position, default_config_key=None, **kwargs):
        """ Base class for Basic entities.

        Basic entities are non-interactive entities.

        Args:
            initial_position: Initial position of the entity.
                Can be list [x,y,theta], AreaPositionSampler or Trajectory.
            default_config_key: default configurations.
                Can be circle, square, rectangle, pentagon, hexagon.
            **kwargs: other params to configure entity.
                Refer to Entity class for physical properties.

        """

        default_config = self._parse_configuration('basic', default_config_key)
        entity_params = {**default_config, **kwargs}

        super(Basic, self).__init__(initial_position=initial_position, **entity_params)


class Door(SceneElement):
    """ Door that can be opened with a switch.

    Properties:
        opened: True if the door is opened.
    """

    entity_type = 'door'

    def __init__(self, initial_position, **kwargs):

        default_config = self._parse_configuration('interactive', 'door')
        entity_params = {**default_config, **kwargs}

        super(Door, self).__init__(initial_position=initial_position, **entity_params)

        self.opened = False


    @property
    def opened(self):
        """ State of the door. True if door is opened."""
        return self._opened

    @opened.setter
    def opened(self, open_):
        self._opened = open_

    def reset(self):

        self.opened = False
        super().reset()
