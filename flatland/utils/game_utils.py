from numpy import random


def generate_position(position):

    if position['type'] == 'fixed':
        pos = position['coordinates']

    elif position['type'] == 'random_in_area':
        min_x, max_x = position['x_range']
        min_y, max_y = position['y_range']
        min_angle, max_angle = position['angle_range']
        pos = [
            min_x + random.rand() * (max_x - min_x),
            min_y + random.rand() * (max_y - min_y),
            min_angle + random.rand() * (max_angle - min_angle),
        ]

    else:
        raise ValueError('Initial position type not implemented: ' + position['type'])

    return pos
