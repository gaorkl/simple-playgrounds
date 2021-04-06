"""
Module for Basic SceneElements
"""
from simple_playgrounds.playgrounds.scene_elements.element import SceneElement
from simple_playgrounds.utils.parser import parse_configuration
from simple_playgrounds.utils.definitions import SceneElementTypes


class Basic(SceneElement):
    """ Basic Scene elements are non-interactive obstacles."""
    visible = True
    entity_type = SceneElementTypes.BASIC

    def __init__(self, default_config_key=None, **kwargs):
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

        default_config = parse_configuration('element_basic', default_config_key)
        entity_params = {**default_config, **kwargs}

        super().__init__(**entity_params)


class Traversable(Basic):
    """ Traversable Scene elements are non-interactive visible and traversable objects."""
    traversable = True


class Wall(Basic):
    """ Wall class"""
    background = True


class Door(SceneElement):
    """ Door that can be opened with a switch.

    Properties:
        opened: True if the door is opened.
    """

    entity_type = SceneElementTypes.DOOR

    def __init__(self, **kwargs):

        default_config = parse_configuration('element_basic', self.entity_type)
        entity_params = {**default_config, **kwargs}

        super().__init__(**entity_params)

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
