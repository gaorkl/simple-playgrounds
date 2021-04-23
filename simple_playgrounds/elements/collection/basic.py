"""
Module for Basic SceneElements
"""
from typing import Union

import pymunk

from simple_playgrounds.elements.element import SceneElement
from simple_playgrounds.configs import parse_configuration
from simple_playgrounds.definitions import ElementTypes


class Physical(SceneElement):

    def __init__(self,
                 config_key: Union[str, ElementTypes],
                 **entity_params,
                 ):
        """

        Args:
            config_key: can be Door, ...
            **kwargs:
        """

        elem_config = parse_configuration('element_basic', config_key)
        elem_config = {**elem_config, **entity_params}

        super().__init__(visible_shape=True, invisible_shape=False, **elem_config)

    def _set_shape_collision(self):
        pass


class Traversable(SceneElement):

    def __init__(self,
                 config_key: Union[str, ElementTypes],
                 **entity_params,
                 ):
        """

        Args:
            config_key: can be Door, ...
            **kwargs:
        """

        elem_config = parse_configuration('element_basic', config_key)
        elem_config = {**elem_config, **entity_params}

        super().__init__(visible_shape=True, invisible_shape=False, traversable=True, **elem_config)

    def _set_shape_collision(self):
        pass


class Wall(Physical):
    """ Wall class"""
    
    def __init__(self,
                 start_point,
                 end_point,
                 wall_depth,
                 **entity_params):

        start_point = pymunk.Vec2d(*start_point)
        end_point = pymunk.Vec2d(*end_point)

        length_wall = int(start_point.get_distance(end_point))

        super().__init__(config_key=ElementTypes.WALL,
                         size=(length_wall, wall_depth),
                         **entity_params)

        self.initial_coordinates = (start_point+end_point)/2, (end_point-start_point).angle


class Door(Physical):
    """ Door that can be opened with a switch.

    Properties:
        opened: True if the door is opened.
    """

    def __init__(self,
                 start_point,
                 end_point,
                 door_depth,
                 **entity_params):
        start_point = pymunk.Vec2d(*start_point)
        end_point = pymunk.Vec2d(*end_point)

        length_wall = int(start_point.get_distance(end_point))

        super().__init__(config_key=ElementTypes.DOOR,
                         size=(length_wall, door_depth),
                         **entity_params)

        self.initial_coordinates = (start_point + end_point) / 2, (end_point - start_point).angle

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
