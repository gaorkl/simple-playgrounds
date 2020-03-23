from flatland.entities.entity import Entity, EntityGenerator
from flatland.utils.config import *

import yaml
import os

__location__ = os.path.realpath(os.path.join(os.getcwd(), os.path.dirname(__file__)))
with open(os.path.join(__location__, 'basic_default.yml'), 'r') as yaml_file:
    default_config = yaml.load(yaml_file)

@EntityGenerator.register_subclass('basic')
class Basic(Entity):

    def __init__(self, custom_config):

        self.entity_type = 'basic'
        super(Basic, self).__init__(custom_config)


@EntityGenerator.register_subclass('rectangle')
class Rectangle(Basic):

    def __init__(self, custom_config):
        custom_config = {**default_config['rectangle'], **custom_config}

        super(Rectangle, self).__init__(custom_config)


@EntityGenerator.register_subclass('circle')
class Circle(Basic):

    def __init__(self, custom_config):
        custom_config = {**default_config['circle'], **custom_config}

        super(Circle, self).__init__(custom_config)

@EntityGenerator.register_subclass('square')
class Square(Basic):

    def __init__(self, custom_config):
        custom_config = {**default_config['square'], **custom_config}

        super(Square, self).__init__(custom_config)


@EntityGenerator.register_subclass('pentagon')
class Pentagon(Basic):

    def __init__(self, custom_config):
        custom_config = {**default_config['pentagon'], **custom_config}

        super(Pentagon, self).__init__(custom_config)


@EntityGenerator.register_subclass('hexagon')
class Hexagon(Basic):

    def __init__(self, custom_config):
        custom_config = {**default_config['hexagon'], **custom_config}

        super(Hexagon, self).__init__(custom_config)



@EntityGenerator.register_subclass('absorbable')
class Absorbable(Entity):

    def __init__(self, custom_config):

        self.entity_type = 'absorbable'

        custom_config = {**default_config['absorbable'], **custom_config}
        super(Absorbable, self).__init__(custom_config)

        self.reward = custom_config['reward']
        self.pm_visible_shape.collision_type = collision_types['contact']

        self.absorbable = True
