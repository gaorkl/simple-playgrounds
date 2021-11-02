import math
import random

from simple_playgrounds.playground.layouts import SingleRoom
from simple_playgrounds.playground.playground import PlaygroundRegister
from simple_playgrounds.element.elements.basic import Physical, Traversable


@PlaygroundRegister.register('profiling', 'basic_unmovable')
class BasicUnmovable(SingleRoom):
    def __init__(self,
                 size,
                 n_elements_per_dim,
                 size_elements,
                 **playground_params):

        super().__init__(size=size, **playground_params)

        basic_cfg_keys = ['rectangle', 'square', 'pentagon', 'triangle', 'hexagon']

        for ind_x in range(n_elements_per_dim):
            for ind_y in range(n_elements_per_dim):

                coord_x = (1+ind_x) * size[0] / (n_elements_per_dim + 1)
                coord_y = (1+ind_x) * size[1] / (n_elements_per_dim + 1)
                orientation = random.uniform(0, 2*math.pi)

                cfg = random.choice(basic_cfg_keys)

                if cfg == 'rectangle':
                    element = Physical(config_key=cfg, name='test', size=(size_elements, size_elements))
                else:
                    element = Physical(config_key=cfg, name='test', radius=size_elements)

                self.add_element(element, initial_coordinates=((coord_x, coord_y), orientation))
