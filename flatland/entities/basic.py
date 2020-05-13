from flatland.entities.entity import Entity, EntityGenerator
from flatland.utils.config import *


@EntityGenerator.register_subclass('basic')
class Basic(Entity):

    visible = True
    entity_type = 'basic'

    def __init__(self, custom_params):

        super(Basic, self).__init__(custom_params)



@EntityGenerator.register_subclass('rectangle')
class Rectangle(Basic):

    def __init__(self, custom_params):

        default_config = self.parse_configuration('basic', 'rectangle')
        entity_params = {**default_config, **custom_params}

        super(Rectangle, self).__init__(entity_params)


@EntityGenerator.register_subclass('circle')
class Circle(Basic):

    def __init__(self, custom_params):

        default_config = self.parse_configuration('basic', 'circle')
        entity_params = {**default_config, **custom_params}

        super(Circle, self).__init__(entity_params)

@EntityGenerator.register_subclass('square')
class Square(Basic):

    def __init__(self, custom_params):

        default_config = self.parse_configuration('basic', 'square')
        entity_params = {**default_config, **custom_params}

        super(Square, self).__init__(entity_params)


@EntityGenerator.register_subclass('pentagon')
class Pentagon(Basic):

    def __init__(self, custom_params):

        default_config = self.parse_configuration('basic', 'pentagon')
        entity_params = {**default_config, **custom_params}

        super(Pentagon, self).__init__(entity_params)


@EntityGenerator.register_subclass('hexagon')
class Hexagon(Basic):

    def __init__(self, custom_params):

        default_config = self.parse_configuration('basic', 'hexagon')
        entity_params = {**default_config, **custom_params}

        super(Hexagon, self).__init__(entity_params)



@EntityGenerator.register_subclass('absorbable')
class Absorbable(Entity):

    entity_type = 'absorbable'
    absorbable = True

    def __init__(self, custom_params):


        default_config = self.parse_configuration('basic', 'absorbable')
        entity_params = {**default_config, **custom_params}

        super(Absorbable, self).__init__(entity_params)

        self.reward = entity_params['reward']
        self.pm_visible_shape.collision_type = collision_types['contact']

