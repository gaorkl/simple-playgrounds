from simple_playgrounds.entities.scene_elements.element import SceneElement
from simple_playgrounds.utils.definitions import CollisionTypes

from abc import ABC


class PassiveSceneElement(SceneElement, ABC):

    interactive = True

    def __init__(self, **kwargs):
        SceneElement.__init__(self, **kwargs)
        self.pm_interaction_shape.collision_type = CollisionTypes.PASSIVE

        self.reward = 0
        self.reward_provided = False

    def pre_step(self):

        self.reward_provided = False

    @property
    def reward(self):

        if not self.reward_provided:
            self.reward_provided = True
            return self._reward

        else:
            return 0

    @reward.setter
    def reward(self, rew):
        self._reward = rew


class TerminationZone(PassiveSceneElement):

    entity_type = 'termination_zone'
    terminate_upon_contact = True
    visible = False

    def __init__(self, initial_position, default_config_key, **kwargs):
        """ Base class for Invisible zones that terminate upon contact

        TerminationZone entities generate a termination of the episode and provide a reward to the agent
        in contact with the entity.

        Args:
            initial_position: initial position of the entity. can be list [x,y,theta], AreaPositionSampler or Trajectory
            default_config_key: default configurations, can be goal_zone or death_zone
            **kwargs: other params to configure entity. Refer to Entity class

        Keyword Args:
            reward: Reward provided.
        """

        default_config = self._parse_configuration('zone', default_config_key)
        entity_params = {**default_config, **kwargs}

        super().__init__(initial_position=initial_position, **entity_params)

        self.reward = entity_params.get('reward', 0)
        self.reward_provided = False


class GoalZone(TerminationZone):

    def __init__(self, initial_position, **kwargs):
        """ Invisible entity that terminates the episode and provides a positive reward to the agent entering the zone

        Default: Invisible Green square of radius 20, reward of 200.

        """

        super().__init__(initial_position=initial_position, default_config_key='goal_zone', **kwargs)


class DeathZone(TerminationZone):

    def __init__(self, initial_position, **kwargs):
        """ Invisible entity that terminates the episode and provides a negative reward to the agent entering the zone

        Default: Invisible Red square of radius 20, reward of -200.

        """

        super().__init__(initial_position=initial_position, default_config_key='death_zone', **kwargs)


class RewardZone(PassiveSceneElement):

    entity_type = 'reward_zone'
    visible = False

    def __init__(self, initial_position, default_config_key, **kwargs):

        """ Base class for zones that provide reward to an agent

        RewardZone entities are invisible zones, which provide a reward to the agent which is inside the zone.

        Args:
            initial_position: initial position of the entity. can be list [x,y,theta], AreaPositionSampler or Trajectory
            default_config_key: default configurations, can be 'fairy' or 'fireball
            **kwargs: other params to configure entity. Refer to Entity class

        Keyword Args:
            reward: Reward provided at each timestep when agent is in the zone
            total_reward: Total reward that the entity can provide during an Episode
        """

        default_config = self._parse_configuration('zone', default_config_key)
        entity_params = {**default_config, **kwargs}

        super().__init__(initial_position=initial_position, **entity_params)

        self.reward = entity_params['reward']

        self.initial_total_reward = entity_params['total_reward']
        self.total_reward = self.initial_total_reward

    @property
    def reward(self):

        if not self.reward_provided:
            self.reward_provided = True

            if self._reward * self.total_reward < 0:
                return 0

            else:
                self.total_reward -= self._reward
                return self._reward

        else:
            return 0

    @reward.setter
    def reward(self, rew):
        self._reward = rew

    def reset(self):
        self.total_reward = self.initial_total_reward
        super().reset()


class ToxicZone(RewardZone):

    def __init__(self, initial_position, **kwargs):
        """ ToxicZone is an invisible entity that provides a reward to an agent which is in the zone.

        Provides a negative reward for each timestep when an agent is in the zone.
        Default: Yellow square of radius 15, reward -1 and total_reward -1000000

        """

        super(ToxicZone, self).__init__(initial_position=initial_position, default_config_key='toxic_zone', **kwargs)


class HealingZone(RewardZone):

    def __init__(self, initial_position, **kwargs):
        """ HealingZone is an invisible entity that provides a reward to an agent which is in the zone.

        Provides a positive reward for each timestep when an agent is in the zone.
        Default: Blue square of radius 15, reward 1 and total_reward  100000

        """
        super(HealingZone, self).__init__(initial_position=initial_position, default_config_key='healing_zone',
                                          **kwargs)
