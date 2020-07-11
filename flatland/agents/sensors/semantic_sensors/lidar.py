from .semantic_sensor import SemanticSensor
from ....utils.definitions import SensorModality
from collections import namedtuple

import pymunk
import math
from operator import attrgetter


LidarPoint = namedtuple('Point', 'entity distance angle')

class Lidar(SemanticSensor):

    sensor_modality = SensorModality.GEOMETRIC

    sensor_type = 'lidar'

    def __init__(self, anchor, invisible_elements, **sensor_params):

        default_config = self.parse_configuration(self.sensor_type)
        sensor_params = {**default_config, **sensor_params}

        super().__init__(anchor, invisible_elements, **sensor_params)

        # Field of View of the Sensor
        self.fovRange = sensor_params.get('range')
        self.fovAngle = sensor_params.get('fov') * math.pi / 180
        self.number_rays = sensor_params['number_rays']

        if self.number_rays == 1:
            self.angles = [0]
        else:
            self.angles = [n * self.fovAngle / (self.number_rays - 1) - self.fovAngle / 2 for n in range(self.number_rays)]
        self.filter = pymunk.ShapeFilter(mask=pymunk.ShapeFilter.ALL_MASKS ^ 0b1)

    def update_sensor(self, pg):

        self.sensor_value = {}

        for sensor_angle in self.angles:

            position = self.anchor.pm_body.position
            angle = self.anchor.pm_body.angle + sensor_angle

            position_end = ( position[0] + self.fovRange * math.cos(angle),
                             position[1] + self.fovRange * math.sin(angle)
                             )

            collisions = pg.space.segment_query(position, position_end, 10, self.filter)

            shapes = [collision.shape for collision in collisions]
            distances = [collision.alpha * self.fovRange for collision in collisions]

            entities = [pg.get_entity_from_shape(shape) for shape in shapes ]
            entities = list(set([ LidarPoint(ent, dist, sensor_angle) for ent, dist in zip(entities, distances)
                                  if ent is not None and ent.pm_visible_shape is not None]))

            agents = [pg.get_agent_from_shape(shape) for shape in shapes ]
            agents = [LidarPoint(ag, dist, sensor_angle) for ag, dist in zip(agents, distances) if ag is not None]
            agents = list(set([ pt for pt in agents if (len(set(pt.entity.body_parts) & set(self.invisible_elements)) == 0)]))

            self.sensor_value[sensor_angle] = entities + agents


    @property
    def shape(self):
        return None


class LidarOcclusion(Lidar):

    def __init__(self, anchor, invisible_elements, **sensor_params):

        super().__init__(anchor, invisible_elements, **sensor_params)

    def update_sensor(self, pg):

        super().update_sensor(pg)

        for angle, points in self.sensor_value.items():


            if points != []:
                min_distance_point = min( points, key=attrgetter('distance') )
                self.sensor_value[angle] = [min_distance_point]

            else:
                self.sensor_value[angle] = []


class LidarOcclusionUnique(LidarOcclusion):

    def __init__(self, anchor, invisible_elements, **sensor_params):

        super().__init__(anchor, invisible_elements, **sensor_params)

    def update_sensor(self, pg):

        super().update_sensor(pg)

        unique_points = {}

        all_points = []

        for angle, points in self.sensor_value.items():
            all_points += points

        for point in all_points:

            min_distance_point = min( [ pt for pt in all_points if pt.entity is point.entity], key=attrgetter('distance') )

            unique_points[min_distance_point.angle] = [min_distance_point]

        self.sensor_value = unique_points
