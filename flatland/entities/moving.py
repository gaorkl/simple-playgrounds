from flatland.entities.entity import Entity, EntityGenerator
from flatland.utils.config import collision_types

class MovingVisibleRewardZone(Entity):

    def __init__(self, entity_params ):
        """
        Instantiate an obstacle with the following parameters
        :param pos: 2d tuple or 'random', position of the fruit
        :param environment: the environment calling the creation of the fruit
        """

        entity_params['visible'] = True
        entity_params['interactive'] = True
        entity_params['movable'] = True

        if 'center_trajectory' in entity_params:
            entity_params['trajectory']['center'] = entity_params['center_trajectory']
        elif 'waypoints' in entity_params:
            entity_params['trajectory']['waypoints'] = entity_params['waypoints']
        else:
            raise ValueError('Trajectory not defined correctly')


        super(MovingVisibleRewardZone, self).__init__(entity_params)

        self.pm_interaction_shape.collision_type = collision_types['zone']

        self.reward = entity_params['reward']
        self.total_reward = entity_params['total_reward']
        self.reward_provided = False

    def pre_step(self):

        self.reward_provided = False

    def get_reward(self):

        if not self.reward_provided:
            self.reward_provided = True

            if self.reward < 0 and self.total_reward > 0:

                return 0

            elif self.reward > 0 and self.total_reward < 0:

                return 0

            else:
                self.total_reward -= self.reward
                return self.reward

        else:
            return 0

    def reset(self):

        self.reward_provided = False
        self.total_reward = self.params['total_reward']

        replace = super().reset()

        return replace


@EntityGenerator.register_subclass('fairy')
class Fairy(MovingVisibleRewardZone):

    def __init__(self, custom_params):

        self.entity_type = 'fairy'

        default_config = self.parse_configuration('moving', 'fairy')
        entity_params = {**default_config, **custom_params}

        super(Fairy, self).__init__(entity_params)


@EntityGenerator.register_subclass('fireball')
class Fireball(MovingVisibleRewardZone):

    def __init__(self, custom_params):

        self.entity_type = 'fireball'

        default_config = self.parse_configuration('moving', 'fireball')
        entity_params = {**default_config, **custom_params}


        super(Fireball, self).__init__(entity_params)
