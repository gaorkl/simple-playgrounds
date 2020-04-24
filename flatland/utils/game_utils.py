import numpy as np
import random, math

class AreaSampler:

    def __init__(self, area_params):

        self.area_shape = area_params['area_shape']
        self.distribution = area_params['distribution']
        self.center = area_params['center']

        # Area shape
        if self.area_shape == 'rectangle':
            self.width, self.length = area_params['shape']

        elif self.area_shape == 'circle':
            self.radius = area_params['radius']

        else:
            raise ValueError('area shape not implemented')

        # Distribution of positions
        if self.distribution == 'gaussian':
            self.variance = area_params['variance']


    def sample(self):

        if self.area_shape == 'rectangle':

            if self.distribution == 'uniform':

                x = random.uniform( self.center[0] - self.width/2 ,self.center[0] + self.width/2 )
                y = random.uniform( self.center[1] - self.length/2 ,self.center[1] + self.length/2 )
                theta = random.uniform( -math.pi, math.pi )

            elif self.distribution == 'gaussian':

                pass


        return x,y,theta


def generate_position(position):

    if isinstance(position, tuple) or isinstance(position, list):
        pos = position

    elif position['type'] == 'fixed':
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
