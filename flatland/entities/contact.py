from flatland.utils.config import *
from flatland.entities.entity import Entity, EntityGenerator

import yaml, os

__location__ = os.path.realpath(os.path.join(os.getcwd(), os.path.dirname(__file__)))
with open(os.path.join(__location__, 'contact_default.yml'), 'r') as yaml_file:
    default_config = yaml.load(yaml_file)

@EntityGenerator.register_subclass('contact_endzone')
class ContactEndZone(Entity):

    def __init__(self, custom_config):

        self.entity_type = 'contact_endzone'

        custom_config = {**default_config['contact_endzone'], **custom_config}

        super(ContactEndZone, self).__init__(custom_config)

        self.reward = custom_config['reward']
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
