import numpy as np
import random

def generate_position(position):

    if position['type'] == 'fixed':
        pos = position['coordinates']

    elif position['type'] == 'circle':
        # For the distribution to be uniform the simplest method is to do a rejection sampling
        reject = True
        while reject:
            center_x, center_y = position['center']
            radius = position['radius']
            min_x, max_x = center_x - radius, center_x + radius
            min_y, max_y = center_y - radius, center_y + radius
            min_angle, max_angle = position['angle_range']
            pos = [
                min_x + np.random.rand() * (max_x - min_x),
                min_y + np.random.rand() * (max_y - min_y),
                min_angle + np.random.rand() * (max_angle - min_angle),
            ]
            reject = (pos[0] - center_x)**2 + (pos[1] - center_y)**2 > radius**2

    elif position['type'] == 'rectangle':
        min_x, max_x = position['x_range']
        min_y, max_y = position['y_range']
        min_angle, max_angle = position['angle_range']
        pos = [
            random.uniform(min_x, max_x),
            random.uniform(min_y, max_y),
            random.uniform(min_angle, max_angle),
        ]

    elif position['type'] == 'list':
        p = np.array([item['probability'] for item in position['list']])
        ps = np.cumsum(p)
        total = np.sum(p)
        x = np.random.rand()*total
        i = 0
        while x > ps[i]:
            i += 1
        pos = generate_position(position['list'][i])

    else:
        raise ValueError('Initial position type not implemented: ' + position['type'])

    return pos
