from flatland.entities.entity import Entity, EntityGenerator
from flatland.utils.config import collision_types

class TerminationZone(Entity):
    """ Invisible Zone that terminates the current game and provide a reward to the agent entering the zone

    Attributes
    ----------
    reward: float
        Reward provided to the agent
    reward_provided: bool
        Indicates whether reward was given to the agent

    """

    def __init__(self, entity_params):
        """ Initialized with a dictionary of parameters

        This base class is used to define the behavior of invisible zones which terminate the game when entered by an agent.
        Entity parameters are used, as well as parameters specific to TerminationZone

        """

        self.entity_type = 'termination_zone'
        self.visible = False
        self.interactive = True

        super(TerminationZone, self).__init__(entity_params)

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

        replace = super().reset()

        return replace


@EntityGenerator.register_subclass('goal_zone')
class GoalZone(TerminationZone):
    """ TerminationZone that provides a positive reward to the agent
    """

    def __init__(self, custom_params):
        """

        :param custom_params:
        """

        default_config = self.parse_configuration('zone', 'goal_zone')
        entity_params = {**default_config, **custom_params}

        super(GoalZone, self).__init__(entity_params)


@EntityGenerator.register_subclass('death_zone')
class DeathZone(TerminationZone):
    ''' TerminationZone that provides a negative reward to the agent
    '''

    def __init__(self, custom_params):
        default_config = self.parse_configuration('zone', 'death_zone')
        entity_params = {**default_config, **custom_params}

        super(DeathZone, self).__init__(entity_params)


class RewardZone(Entity):

    def __init__(self, entity_params):

        self.entity_type = 'reward_zone'
        self.visible = False
        self.interactive = True

        super(RewardZone, self).__init__(entity_params)
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

        replace = super().reset()

        return replace

@EntityGenerator.register_subclass('toxic_zone')
class ToxicZone(RewardZone):

    def __init__(self, custom_params):


        default_config = self.parse_configuration('zone', 'toxic_zone')
        entity_params = {**default_config, **custom_params}

        super(ToxicZone, self).__init__(entity_params)


@EntityGenerator.register_subclass('healing_zone')
class HealingZone(RewardZone):

    def __init__(self, custom_params):
        default_config = self.parse_configuration('zone', 'healing_zone')
        entity_params = {**default_config, **custom_params}

        super(HealingZone, self).__init__(entity_params)