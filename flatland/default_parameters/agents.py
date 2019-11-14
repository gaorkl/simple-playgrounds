import math

"""
Different standard parameters for frames:
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

arms_texture = {
    'type': 'color',
    'color': (250, 0, 250)
}

metabolism_default = {
    'health' : 1000,
    'latent_metabolism' : 0.001,
    'base_metabolism' : 0.01,
    'action_metabolism': 0.1,
    'head_metabolism': 0.005,
}

#####################
# Sensors

rgb_default = {
    'type': 'rgb',
    'fovResolution': 128,
    'fovRange': 600,
    'fovAngle': math.pi,
    'bodyAnchor': "base",
}

touch_default = {
    'type': 'touch',
    'fovResolution': 128,
    'contactRange': 10,
    'fovAngle': 2*math.pi,
    'bodyAnchor': "base",
}

#####################
# Frames

forward_default = {
    'base_texture':  base_texture,
    'base_radius': 25,
    'base_mass' : 20,

    'base_translation_speed': 1.0,
    'base_rotation_speed': 0.25,

}

holonomic_default = forward_default.copy()

forward_head_default = {
    'head_texture':  head_texture,
    'head_radius': 8,
    'head_mass' : 5,

    'head_rotation_speed': 0.25,
    'head_rotation_range': math.pi/2,
    'head_metabolism' : 0.001,

}

forward_head_default = {**forward_default, **forward_head_default}


forward_head_arms_default = {
    'arm_texture':  arms_texture,
    'arm_radius': 10,
    'arm_mass' : 1,

    'arm_rotation_speed': 0.25,
    'arm_rotation_range': math.pi/3,
    'arm_metabolism' : 0.001,

}

forward_head_arm_default = {**forward_head_default, **forward_head_arms_default}

