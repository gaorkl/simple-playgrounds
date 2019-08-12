import math

"""
Different standard parameters for agents:
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


forward_default = {
    'base_texture':  base_texture,
    'base_radius': 20,
    'base_mass' : 20,

    'base_translation_speed': 1.0,
    'base_rotation_speed': 0.1,

    'health' : 1000,
    'base_metabolism' : 0.001,
    'action_metabolism': 0.01,

    'sensors':
        [
            {
                'name': 'rgb_1',
                'type': 'rgb',
                'fovResolution': 128,
                'fovRange': 100,
                'fovAngle': math.pi,
                'bodyAnchor': "base",
                'd_r': 0,
                'd_theta': 0,
                'd_relativeOrientation': 0
            },

            {
                'name': 'touch_1',
                'type': 'touch',
                'fovResolution': 128,
                'fovRange': 25,
                'fovAngle': 2*math.pi,
                'bodyAnchor': "base",
                'd_r': 0,
                'd_theta': 0,
                'd_relativeOrientation': 0
            }
        ]

}


holonomic_default = forward_default.copy()

forward_head_default = {
    'head_texture':  head_texture,
    'head_radius': 15,
    'head_mass' : 5,

    'head_rotation_speed': 0.1,
    'head_rotation_range': math.pi/2,
    'head_metabolism' : 0.001,

    'sensors':
        [
            {
                'name': 'rgb_1',
                'type': 'rgb',
                'fovResolution': 128,
                'fovRange': 100,
                'fovAngle': math.pi,
                'bodyAnchor': "head",
                'd_r': 0,
                'd_theta': 0,
                'd_relativeOrientation': 0
            },

            {
                'name': 'touch_1',
                'type': 'touch',
                'fovResolution': 128,
                'fovRange': 25,
                'fovAngle': 2*math.pi,
                'bodyAnchor': "base",
                'd_r': 0,
                'd_theta': 0,
                'd_relativeOrientation': 0
            }
        ]

}

forward_head_default = {**forward_default, **forward_head_default}
