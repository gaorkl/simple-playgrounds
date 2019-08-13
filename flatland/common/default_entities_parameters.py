import math

"""
Different standard parameters for entities
"""

# Edibles

edible_texture =  {
    'type': 'color',
    'color': (200, 100, 50)
    }

edible_default = {
    'physical_shape': 'circle',
    'radius': 10,
    'mass': 10,
    'texture': edible_texture,
    'movable': True,

    'entity_type':'actionable',
    'actionable_type': 'edible',
    'action_radius': 10,
    'shrink_when_eaten': 0.9,

    'initial_reward': 30
}