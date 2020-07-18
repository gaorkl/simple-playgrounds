"""
Module for Gem SceneElements.
Gem interacts with other SceneElements.
"""
from simple_playgrounds.entities.scene_elements.element import SceneElement
from simple_playgrounds.utils import CollisionTypes


class GemSceneElement(SceneElement):
    """
    A Gem interacts with other SceneElements.
    """

    entity_type = 'gem'
    movable = True

    def __init__(self, initial_position, **kwargs):

        SceneElement.__init__(self, initial_position=initial_position, **kwargs)
        self.pm_visible_shape.collision_type = CollisionTypes.GEM


class Coin(GemSceneElement):

    """Coins are used with a VendingMachine to get rewards.
    A Coin disappears when in contact with its VendingMachine."""

    entity_type = 'coin'
    movable = True

    def __init__(self, initial_position, **kwargs):
        """
        Default: Gold circle of radius 5 and mass 5, movable.
        """

        default_config = self._parse_configuration('interactive', 'coin')
        entity_params = {**default_config, **kwargs}

        super(Coin, self).__init__(initial_position=initial_position, **entity_params)


class Key(GemSceneElement):

    """Keys are used to open Chests or Doors.
    A Key disappears when in contact with its VendingMachine."""

    entity_type = 'key'
    movable = True

    def __init__(self, initial_position, **kwargs):
        """
        Default: Grey hexagon of radius 8 and mass 5, movable.
        """

        default_config = self._parse_configuration('interactive', 'key')
        entity_params = {**default_config, **kwargs}

        super(Key, self).__init__(initial_position=initial_position, **entity_params)
