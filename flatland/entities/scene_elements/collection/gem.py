from flatland.entities.scene_elements.element import SceneElement
from flatland.utils import CollisionTypes


class GemSceneElement(SceneElement):

    entity_type = 'gem'
    movable = True

    def __init__(self, initial_position, **kwargs):

        SceneElement.__init__(self, initial_position=initial_position, **kwargs)
        self.pm_visible_shape.collision_type = CollisionTypes.GEM


class Coin(GemSceneElement):

    entity_type = 'coin'
    movable = True

    def __init__(self, initial_position, **kwargs):
        """ Coins are used with a VendingMachine to get rewards.

        Default: Gold circle of radius 5 and mass 5.

        Args:
            initial_position: initial position of the entity. can be list [x,y,theta], AreaPositionSampler or Trajectory
            **kwargs: other params to configure entity. Refer to Entity class
        """

        default_config = self._parse_configuration('interactive', 'coin')
        entity_params = {**default_config, **kwargs}

        super(Coin, self).__init__(initial_position=initial_position, **entity_params)




class Key(GemSceneElement):

    entity_type = 'key'
    movable = True

    def __init__(self, initial_position, **kwargs):
        """ Key entity to open chest

        Default: Grey hexagon of radius 8 and mass 5, movable

        Args:
            initial_position: initial position of the entity. can be list [x,y,theta], AreaPositionSampler or Trajectory
            **kwargs: other params to configure entity. Refer to Entity class
        """

        default_config = self._parse_configuration('interactive', 'key')
        entity_params = {**default_config, **kwargs}

        super(Key, self).__init__(initial_position=initial_position, **entity_params)

