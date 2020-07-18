from simple_playgrounds.entities.scene_elements.collection.passive import PassiveSceneElement


class VisibleRewardZone(PassiveSceneElement):

    interactive = True
    entity_type = 'reward_zone'

    def __init__(self, initial_position, default_config_key=None, **kwargs):
        """ Base class for entities that provide reward to an agent in its proximity

        VisibleRewardZone entities provide a reward to the agent
        in close proximity with the entity.

        Args:
            initial_position: initial position of the entity. can be list [x,y,theta], AreaPositionSampler or Trajectory
            default_config_key: default configurations, can be 'fairy' or 'fireball
            **kwargs: other params to configure entity. Refer to Entity class

        Keyword Args:
            reward: Reward provided at each timestep when agent is in proximity
            total_reward: Total reward that the entity can provide during an Episode
        """

        default_config = self._parse_configuration('proximity', default_config_key)
        entity_params = {**default_config, **kwargs}

        super(VisibleRewardZone, self).__init__(initial_position=initial_position, **entity_params)

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

        self.reward_provided = False
        self.total_reward = self.initial_total_reward

        super().reset()


class Fairy(VisibleRewardZone):

    def __init__(self, initial_position, **kwargs):
        """ Fairy entities provide a reward to an agent which is in proximity

        Provides a positive reward of 2 for each timestep when an agent is in proximity
        Default: Turquoise-blue circle of radius 8, reward 2 and total_reward 200

        """
        super(Fairy, self).__init__(initial_position=initial_position, default_config_key='fairy', **kwargs)


class Fireball(VisibleRewardZone):

    def __init__(self, initial_position, **kwargs):
        """ Fireball entities provide a negative reward to an agent which is in proximity

        Provides a negative reward of 2 for each timestep when an agent is in proximity
        Default: Red circle of radius 8, reward -2 and total_reward -200

        """
        super(Fireball, self).__init__(initial_position=initial_position, default_config_key='fireball', **kwargs)
