import math

"""
Different standard parameters for scene_layouts
"""

walls_texture = {
    'type': 'uniform_grained',
    'min': [140, 140, 0],
    'max': [160, 160, 0],
    'size_grains': 4
}

basic_scene_default = {
    'scene_type': 'basic',
    'scene_shape': (400, 400),
    'walls_depth': 10,
    'walls_texture': walls_texture.copy()
    }

two_rooms_scene_default = {
    'scene_type': 'two_rooms',
    'scene_shape': (400, 800),
    'walls_depth': 10,
    'walls_texture': walls_texture.copy(),
    'doorstep_type': 'random',
    'doorstep_size' : 100
    }