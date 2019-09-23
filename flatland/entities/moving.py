from flatland.default_parameters.entities import *
from flatland.entities.entity import Entity, EntityGenerator
from flatland.utils.config import collision_types

class MovingVisibleRewardZone(Entity):

    def __init__(self, params ):
        """
        Instantiate an obstacle with the following parameters
        :param pos: 2d tuple or 'random', position of the fruit
        :param environment: the environment calling the creation of the fruit
        """

        params['visible'] = True
        params['interactive'] = True

        super(MovingVisibleRewardZone, self).__init__(params)

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

        else:
            return 0

@EntityGenerator.register_subclass('fairy')
class Fairy(MovingVisibleRewardZone):

    def __init__(self, params):

        params = {**fairy_default, **params}

        super(Fairy, self).__init__(params)


@EntityGenerator.register_subclass('fireball')
class Fireball(MovingVisibleRewardZone):

    def __init__(self, params):
        params = {**fairy_default, **params}

        super(Fireball, self).__init__(params)
