from flatland.entities.entity import Entity, EntityGenerator
from flatland.utils.config import collision_types

class VisibleRewardZone(Entity):

    interactive = True
    entity_type = 'reward_zone'

    def __init__(self, initial_position, default_config_key = None, **kwargs):
        """
        Instantiate an obstacle with the following parameters
        :param pos: 2d tuple or 'random', position of the fruit
        :param environment: the environment calling the creation of the fruit
        """

        default_config = self.parse_configuration('proximity', default_config_key)
        entity_params = {**default_config, **kwargs}

        super(VisibleRewardZone, self).__init__(initial_position=initial_position, **entity_params)

        self.pm_interaction_shape.collision_type = collision_types['zone']

        self.reward = entity_params['reward']
        self.initial_total_reward = entity_params['total_reward']
        self.total_reward = self.initial_total_reward
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
        self.total_reward = self.initial_total_reward

        super().reset()



class Fairy(VisibleRewardZone):

    def __init__(self, initial_position, **kwargs):

        super(Fairy, self).__init__(initial_position=initial_position, default_config_key='fairy', **kwargs)


class Fireball(VisibleRewardZone):

    def __init__(self, initial_position, **kwargs):

        super(Fireball, self).__init__(initial_position=initial_position, default_config_key='fireball', **kwargs)
