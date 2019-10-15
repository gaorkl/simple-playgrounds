import math

"""
Different standard parameters for scene_layouts
"""

walls_texture = {
    'type': 'random_tiles',
    'min': [140, 140, 0],
    'max': [160, 160, 0],
    'size_tiles': 4
}

room_scene_default = {
    'scene_type': 'room',
    'room_shape': (200, 200),
    'walls_depth': 10,
    'walls_texture': walls_texture.copy()
    }

linear_rooms_scene_default = {
    'scene_type': 'linear_rooms',
    'room_shape': (200, 300),
    'number_rooms': 2,
    'walls_depth': 10,
    'walls_texture': walls_texture.copy(),
    'doorstep_type': 'random',
    'doorstep_size' : 50
    }
