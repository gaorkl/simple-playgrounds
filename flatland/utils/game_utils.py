from numpy import random


def generate_position(position):

    if position['type'] == 'fixed':
        pos = position['coordinates']

    elif position['type'] == 'area':
        min_x, max_x = position['x_range']
        min_y, max_y = position['y_range']
        min_angle, max_angle = position['angle_range']
        pos = [
            min_x + random.rand() * (max_x - min_x),
            min_y + random.rand() * (max_y - min_y),
            min_angle + random.rand() * (max_angle - min_angle),
        ]

    elif position['type'] == 'list_fixed':
        n = len(position['list'])
        i = random.randint(0, n)
        pos = position['list'][i]

    elif position['type'] == 'list_areas':
        n = len(position['list'])
        i = random.randint(0, n)
        min_x, max_x = position['list'][i]['x_range']
        min_y, max_y = position['list'][i]['y_range']
        min_angle, max_angle = position['list'][i]['angle_range']
        pos = [
            min_x + random.rand() * (max_x - min_x),
            min_y + random.rand() * (max_y - min_y),
            min_angle + random.rand() * (max_angle - min_angle),
        ]

    else:
        raise ValueError('Initial position type not implemented: ' + position['type'])

    return pos
