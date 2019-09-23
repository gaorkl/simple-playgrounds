from .entity import *
from flatland.default_parameters.entities import *
from flatland.utils.config import collision_types

@EntityGenerator.register_subclass('end_zone')
class EndZone(Entity):

    def __init__(self, params):

        params = {**zone_default, **params}
        params['visible'] = False
        params['interactive'] = True

        super(EndZone, self).__init__(params)
        self.pm_interaction_shape.collision_type = collision_types['zone']

        self.reward = params.get('reward', 0)
        self.reward_provided = False


    def pre_step(self):

        self.reward_provided = False

    def get_reward(self):

        if not self.reward_provided:
            self.reward_provided = True
            return self.reward

        else:
            return 0

@EntityGenerator.register_subclass('reward_zone')
class RewardZone(Entity):

    def __init__(self, params):

        params = {**zone_default, **params}
        params['visible'] = False
        params['interactive'] = True

        super(RewardZone, self).__init__(params)
        self.pm_interaction_shape.collision_type = collision_types['zone']

        self.reward = params['reward']
        self.total_reward = params['total_reward']
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

        else: return 0


