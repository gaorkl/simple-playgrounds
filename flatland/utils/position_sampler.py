
import numpy as np
import random, math

class PositionAreaSampler:

    def __init__(self, **area_params):

        self.area_shape = area_params['area_shape']
        self.center = area_params['center']

        self.theta_min, self.theta_max = area_params.get('theta_range', [-math.pi, math.pi])

        # Area shape
        if self.area_shape == 'rectangle':
            self.width, self.length = area_params['shape']

        elif self.area_shape == 'circle':
            self.radius = area_params['radius']

        elif self.area_shape == 'gaussian':
            self.radius = area_params['radius']
            self.variance = area_params['variance']

        else:
            raise ValueError('area shape not implemented')


    def sample(self, center = None):

        if center is not None:
            self.center = center

        if self.area_shape == 'rectangle':
            x = random.uniform( self.center[0] - self.width/2 ,self.center[0] + self.width/2 )
            y = random.uniform( self.center[1] - self.length/2 ,self.center[1] + self.length/2 )
            theta = random.uniform( self.theta_min, self.theta_max )


        elif self.area_shape == 'circle':

            x = math.inf

            y = math.inf

            theta = random.uniform(self.theta_min, self.theta_max)

            while ((x - self.center[0]) ** 2 + (y - self.center[1]) ** 2 > self.radius ** 2):
                x = random.uniform(self.center[0] - self.radius / 2, self.center[0] + self.radius / 2)

                y = random.uniform(self.center[1] - self.radius / 2, self.center[1] + self.radius / 2)

        elif self.area_shape == 'gaussian':

            x = math.inf
            y = math.inf
            theta = random.uniform(self.theta_min, self.theta_max)

            while ( (x - self.center[0])**2 + (y - self.center[1])**2 > self.radius**2):

                x, y = np.random.multivariate_normal(self.center, [[self.variance, 0], [0, self.variance]] )

        return [x,y,theta]


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

# Trajectory
# if 'center_trajectory' in entity_params:
#     entity_params['trajectory']['center'] = entity_params['center_trajectory']
# elif 'waypoints' in entity_params:
#     entity_params['trajectory']['waypoints'] = entity_params['waypoints']
# else:
#     raise ValueError('Trajectory not defined correctly')
#
# if 'speed' in entity_params:
#     entity_params['trajectory']['speed'] = entity_params['speed']
