from flatland.utils.config import *
from flatland.entities.entity import Entity, EntityGenerator

import yaml, os

__location__ = os.path.realpath(os.path.join(os.getcwd(), os.path.dirname(__file__)))
with open(os.path.join(__location__, 'configs/contact_default.yml'), 'r') as yaml_file:
    default_config = yaml.load(yaml_file)


class TerminationContact(Entity):

    entity_type = 'contact_termination'
    visible = True

    def __init__(self, entity_params):

        super(TerminationContact, self).__init__(entity_params)

        self.reward = entity_params['reward']
        self.pm_visible_shape.collision_type = collision_types['contact']

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


@EntityGenerator.register_subclass('visible_endgoal')
class VisibleEndGoal(TerminationContact):

    def __init__(self, custom_config):
        custom_config = {**default_config['visible_endgoal'], **custom_config}

        super(VisibleEndGoal, self).__init__(custom_config)


@EntityGenerator.register_subclass('visible_deathtrap')
class VisibleDeathTrap(TerminationContact):

    def __init__(self, custom_config):
        custom_config = {**default_config['visible_deathtrap'], **custom_config}

        super(VisibleDeathTrap, self).__init__(custom_config)

