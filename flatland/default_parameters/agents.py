import math

"""
Different standard parameters for physical_bodies:
 - forward_default
 - forward_head_default
 - holonomic_default
"""

base_texture =  {
    'type': 'color',
    'color': (150, 0, 150)
    }

head_texture = {
    'type': 'color',
    'color': (200, 0, 200)
}

metabolism_default = {
    'health' : 1000,
    'base_metabolism' : 0.001,
    'action_metabolism': 0.01,
}

rgb_default = {
    'type': 'rgb',
    'fovResolution': 128,
    'fovRange': 400,
    'fovAngle': math.pi,
    'bodyAnchor': "base",
}

touch_default = {
    'type': 'touch',
    'fovResolution': 128,
    'fovRange': 5,
    'fovAngle': 2*math.pi,
    'bodyAnchor': "base",
}


forward_default = {
    'base_texture':  base_texture,
    'base_radius': 20,
    'base_mass' : 20,

    'base_translation_speed': 10.0,
    'base_rotation_speed': 0.1,

}

holonomic_default = forward_default.copy()

forward_head_default = {
    'head_texture':  head_texture,
    'head_radius': 10,
    'head_mass' : 5,

    'head_rotation_speed': 0.1,
    'head_rotation_range': math.pi/2,
    'head_metabolism' : 0.001,

}

forward_head_default = {**forward_default, **forward_head_default}
