"""
Module for Basic SceneElements
"""
from simple_playgrounds.scene_elements.element import SceneElement
from simple_playgrounds.utils.parser import parse_configuration
from simple_playgrounds.utils.definitions import ElementTypes





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

    entity_type = ElementTypes.DOOR

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
