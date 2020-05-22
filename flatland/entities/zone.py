from flatland.entities.entity import Entity
from flatland.utils.config import collision_types

class TerminationZone(Entity):


    entity_type = 'termination_zone'
    visible = False
    interactive = True


    def __init__(self, initial_position, default_config_key, **kwargs):

        default_config = self.parse_configuration('zone', default_config_key)
        entity_params = {**default_config, **kwargs}

        super(TerminationZone, self).__init__(initial_position = initial_position, **entity_params)

        self.pm_interaction_shape.collision_type = collision_types['zone']

        self.reward = entity_params.get('reward', 0)
        self.reward_provided = False


    def pre_step(self):

        self.reward_provided = False

    def get_reward(self):

        if not self.reward_provided:
            self.reward_provided = True
            return self.reward

        else:
            return 0

    def reset(self):

        self.reward_provided = False

        super().reset()



class GoalZone(TerminationZone):

    def __init__(self,initial_position, **kwargs):

        super(GoalZone, self).__init__(initial_position=initial_position, default_config_key = 'goal_zone', **kwargs)


class DeathZone(TerminationZone):

    def __init__(self, initial_position, **kwargs):
        super(DeathZone, self).__init__(initial_position=initial_position, default_config_key='death_zone', **kwargs)



class RewardZone(Entity):

    entity_type = 'reward_zone'
    visible = False
    interactive = True

    def __init__(self, initial_position, default_config_key , **kwargs):

        default_config = self.parse_configuration('zone', default_config_key)
        entity_params = {**default_config, **kwargs}

        super(RewardZone, self).__init__(initial_position=initial_position, **entity_params)

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

        else: return 0

    def reset(self):
        self.total_reward = self.initial_total_reward
        self.reward_provided = False

        super().reset()


class ToxicZone(RewardZone):

    def __init__(self,initial_position, **kwargs):

        super(ToxicZone, self).__init__(initial_position=initial_position, default_config_key = 'toxic_zone', **kwargs)

class HealingZone(RewardZone):

    def __init__(self,initial_position, **kwargs):

        super(HealingZone, self).__init__(initial_position=initial_position, default_config_key = 'healing_zone', **kwargs)

