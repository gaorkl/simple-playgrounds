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

    'entity_type':'edible',
    'interaction_range': 10,
    'shrink_when_eaten': 0.9,
    'min_reward': 5,

    'initial_reward': 30
}

# Basic entities

basic_texture =  {
    'type': 'color',
    'color': (125, 100, 150)
    }

basic_default = {
    'physical_shape': 'circle',
    'radius': 10,
    'mass': 10,
    'texture': basic_texture,
    'movable': True
}

# Absorbables

absorbable_texture =  {
    'type': 'color',
    'color': (250, 00, 50)
    }

absorbable_default = {
    'physical_shape': 'triangle',
    'radius': 5,
    'mass': 5,
    'texture': absorbable_texture,
    'movable': True,
    'entity_type' : 'absorbable',
    'reward' : 15

}

# Dispenser
dispenser_texture =  {
    'type': 'color',
    'color': (50, 100, 200)
    }

dispenser_default = {
    'physical_shape': 'circle',
    'radius': 15,
    'mass': 10,
    'texture': dispenser_texture,
    'movable': False,

    'entity_type':'actionable',
    'actionable_type': 'dispenser',
    'action_radius': 10,

    'object_produced': absorbable_default,
    'area_shape': 'rectangle',
    'limit': 15

}

# Yielder

yielder_default = {

    'entity_type':'yielder',
    'object_produced': absorbable_default,
    'area_shape': 'rectangle',
    'limit': 10,
    'probability': 0.1

}

# Graspable

graspable_texture =  {
    'type': 'color',
    'color': (250, 0, 250)
    }

graspable_default = {

    'physical_shape': 'pentagon',
    'radius': 10,
    'mass': 5,
    'texture': graspable_texture,
    'movable': True,

    'entity_type':'actionable',
    'actionable_type': 'graspable',
    'action_radius': 10,
}

###

door_texture =  {
    'type': 'color',
    'color': (0, 0, 250)
    }

door_default = {
    'physical_shape': 'rectangle',
    'shape_rectangle': [10, 100],
    'texture': door_texture,
    'movable': False
}


door_opener_default = {

    'physical_shape': 'circle',
    'radius': 10,
    'texture': door_texture,
    'movable': False,

    'entity_type':'actionable',
    'actionable_type': 'door_opener',
    'door': door_default,
    'action_radius': 10,
    'time_open': 200
}


# Zones

end_zone_texture =  {
    'type': 'color',
    'color': (0, 250, 0)
    }

end_zone_default = {
    'physical_shape': 'circle',
    'radius': 10,
    'texture': end_zone_texture,

    'entity_type':'zone',
    'zone_type': 'end_zone',
    'reward': 200
}

healing_zone_texture =  {
    'type': 'color',
    'color': (0, 0, 250)
    }

healing_zone_default = {
    'physical_shape': 'circle',
    'radius': 20,
    'texture': healing_zone_texture,

    'entity_type':'zone',
    'zone_type': 'reward_zone',
    'reward': 2,
    'total_reward': 200
}

damaging_zone_texture =  {
    'type': 'color',
    'color': (250, 0, 0)
    }

damaging_zone_default = {
    'physical_shape': 'circle',
    'radius': 20,
    'texture': damaging_zone_texture,

    'entity_type':'zone',
    'zone_type': 'reward_zone',
    'reward': -2,
    'total_reward': -200
}