"""
Module for Basic SceneElements
"""
from typing import Union

from simple_playgrounds.elements.element import SceneElement
from simple_playgrounds.utils.parser import parse_configuration
from simple_playgrounds.utils.definitions import ElementTypes


class Physical(SceneElement):

    def __init__(self,
                 geometric_shape: Union[str, ElementTypes],
                 **kwargs,
                 ):
        """

        Args:
            geometric_shape: can be Door, ...
            **kwargs:
        """

        elem_config = parse_configuration('element_basic', geometric_shape)
        elem_config = {**elem_config, **kwargs}

        super().__init__(visible_shape=True, invisible_shape=False, **elem_config)

    def _set_visible_shape_collision(self):
        pass

    def _set_invisible_shape_collision(self):
        pass


class Traversable(SceneElement):

    def __init__(self,
                 geometric_shape: Union[str, ElementTypes],
                 **kwargs,
                 ):
        """

        Args:
            geometric_shape: can be Door, ...
            **kwargs:
        """

        elem_config = parse_configuration('element_basic', geometric_shape)
        elem_config = {**elem_config, **kwargs}

        super().__init__(visible_shape=True, invisible_shape=False, traversable=True, **elem_config)

    def _set_visible_shape_collision(self):
        pass

    def _set_invisible_shape_collision(self):
        pass


class Wall(Physical):
    """ Wall class"""
    
    def __init__(self, **kwargs):
        super().__init__(ElementTypes.WALL, **kwargs)


class Door(Physical):
    """ Door that can be opened with a switch.

    Properties:
        opened: True if the door is opened.
    """

    def __init__(self, **kwargs):

        super().__init__(ElementTypes.DOOR, **kwargs)
        self._opened = False

    @property
    def opened(self):
        """ State of the door. True if door is opened."""
        return self._opened

    def open(self):
        self._opened = True
        
    def close(self):
        self._opened = False

    def reset(self):
        self.close()
        super().reset()
