from ..entity import Entity
from ...utils import CollisionTypes


class Coin(Entity):

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

        self.pm_visible_shape.collision_type = CollisionTypes.GEM


class Key(Entity):

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

        self.pm_visible_shape.collision_type = CollisionTypes.GEM
