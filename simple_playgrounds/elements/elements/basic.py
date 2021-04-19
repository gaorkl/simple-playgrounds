"""
Module for Basic SceneElements
"""
from typing import Union

import pymunk

from simple_playgrounds.elements.element import SceneElement
from simple_playgrounds.utils.parser import parse_configuration
from simple_playgrounds.utils.definitions import ElementTypes, PhysicalShapes


class Physical(SceneElement):

    def __init__(self,
                 config_key: Union[str, ElementTypes],
                 **kwargs,
                 ):
        """

        Args:
            config_key: can be Door, ...
            **kwargs:
        """

        elem_config = parse_configuration('element_basic', config_key)
        elem_config = {**elem_config, **kwargs}

        super().__init__(visible_shape=True, invisible_shape=False, **elem_config)

    def _set_visible_shape_collision(self):
        pass

    def _set_invisible_shape_collision(self):
        pass


class Traversable(SceneElement):

    def __init__(self,
                 config_key: Union[str, ElementTypes],
                 **kwargs,
                 ):
        """

        Args:
            config_key: can be Door, ...
            **kwargs:
        """

        elem_config = parse_configuration('element_basic', config_key)
        elem_config = {**elem_config, **kwargs}

        super().__init__(visible_shape=True, invisible_shape=False, traversable=True, **elem_config)

    def _set_visible_shape_collision(self):
        pass

    def _set_invisible_shape_collision(self):
        pass


class Wall(Physical):
    """ Wall class"""
    
    def __init__(self,
                 start_point,
                 end_point,
                 wall_depth,
                 **kwargs):

        start_point = pymunk.Vec2d(*start_point)
        end_point = pymunk.Vec2d(*end_point)

        length_wall = int(start_point.get_distance(end_point))

        super().__init__(config_key=ElementTypes.WALL,
                         size=(length_wall, wall_depth),
                         **kwargs)

        self.initial_coordinates = (start_point+end_point)/2, (end_point-start_point).angle

    def _set_visible_shape_collision(self):
        pass

    def _set_invisible_shape_collision(self):
        pass


class Door(Physical):
    """ Door that can be opened with a switch.

    Properties:
        opened: True if the door is opened.
    """

    def __init__(self,
                 start_point,
                 end_point,
                 door_depth,
                 **kwargs):
        start_point = pymunk.Vec2d(*start_point)
        end_point = pymunk.Vec2d(*end_point)

        length_wall = int(start_point.get_distance(end_point))

        super().__init__(config_key=ElementTypes.DOOR,
                         size=(length_wall, door_depth),

                         **kwargs)

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
