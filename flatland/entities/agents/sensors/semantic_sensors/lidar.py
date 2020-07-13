from .semantic_sensor import SemanticSensor
from flatland.utils.definitions import SensorModality
from collections import namedtuple

import pymunk
import math
from operator import attrgetter


LidarPoint = namedtuple('Point', 'entity distance angle')


class LidarRays(SemanticSensor):

    sensor_modality = SensorModality.SEMANTIC

    sensor_type = 'lidar-rays'

    def __init__(self, anchor, invisible_elements, remove_occluded = True, allow_duplicates = False, **sensor_params):

        default_config = self.parse_configuration(self.sensor_type)
        sensor_params = {**default_config, **sensor_params}

        super().__init__(anchor, invisible_elements, remove_occluded = remove_occluded, allow_duplicates = allow_duplicates, **sensor_params)

        # Field of View of the Sensor
        self.fovRange = sensor_params.get('range')
        self.fovAngle = sensor_params.get('fov') * math.pi / 180
        self.number_rays = sensor_params['number_beams']

        self.radius_beam = 1

        if self.number_rays == 1:
            self.angles = [0]
        else:
            self.angles = [n * self.fovAngle / (self.number_rays - 1) - self.fovAngle / 2 for n in range(self.number_rays)]

        self.filter = pymunk.ShapeFilter(mask=pymunk.ShapeFilter.ALL_MASKS ^ 0b1)
        self.sensor_value = {}

    def update_sensor(self, pg):

        self.sensor_value = {}

        for sensor_angle in self.angles:

            position = self.anchor.pm_body.position
            angle = self.anchor.pm_body.angle + sensor_angle

            position_end = ( position[0] + self.fovRange * math.cos(angle),
                             position[1] + self.fovRange * math.sin(angle)
                             )

            collisions = pg.space.segment_query(position, position_end, 2*self.radius_beam, self.filter)

            shapes = [collision.shape for collision in collisions]
            distances = [collision.alpha * self.fovRange for collision in collisions]

            entities_dist = [(pg.get_scene_element_from_shape(shape), dist)
                             for shape, dist in zip(shapes, distances)
                             if shape.sensor == False]

            entities = list(set([ LidarPoint(ent, dist, sensor_angle) for ent, dist in entities_dist
                                  if ent is not None and ent.pm_visible_shape is not None]))

            agents = [pg.get_agent_from_shape(shape) for shape in shapes]
            agents = [LidarPoint(ag, dist, sensor_angle) for ag, dist in zip(agents, distances) if ag is not None]
            agents = list(set([ pt for pt in agents if (len(set(pt.entity.body_parts) & set(self.invisible_elements)) == 0)]))

            self.sensor_value[sensor_angle] = entities + agents

        self.filter_sensor_values()



    @property
    def shape(self):
        return None


class LidarCones(SemanticSensor):

    sensor_modality = SensorModality.SEMANTIC

    sensor_type = 'lidar-cones'

    def __init__(self, anchor, invisible_elements, remove_occluded = True, allow_duplicates = False, **sensor_params):

        default_config = self.parse_configuration(self.sensor_type)
        sensor_params = {**default_config, **sensor_params}

        super().__init__(anchor, invisible_elements, remove_occluded = remove_occluded, allow_duplicates = allow_duplicates, **sensor_params)

        # Field of View of the Sensor
        self.fovRange = sensor_params.get('range')
        self.fovAngle = sensor_params.get('fov') * math.pi / 180
        self.number_cones = sensor_params['number_cones']
        self.remove_occluded = remove_occluded
        self.allow_duplicates = allow_duplicates

        if self.number_cones == 1 and self.fovAngle > math.pi:
            raise ValueError

        self.radius_beam = self.fovRange * self.fovAngle / self.number_cones

        angle = self.fovAngle - self.fovAngle / (self.number_cones)
        self.angles_cone_center = [n * angle / (self.number_cones - 1) - angle / 2 for n in
                       range(self.number_cones)]

        self.angles_segment_r = [ n * self.fovAngle / (self.number_cones) - self.fovAngle / 2 for n in range(self.number_cones)]
        self.angles_segment_l = [ n * self.fovAngle / (self.number_cones) - self.fovAngle / 2 for n in range(1,self.number_cones+1)]

        self.filter = pymunk.ShapeFilter(mask=pymunk.ShapeFilter.ALL_MASKS ^ 0b1)

    def update_sensor(self, pg):

        self.sensor_value = {}

        for cone_angle, l_angle, r_angle in zip(self.angles_cone_center, self.angles_segment_l, self.angles_segment_r):

            position_center = self.anchor.pm_body.position
            angle = self.anchor.pm_body.angle + cone_angle
            position_end_cone = ( position_center[0] + self.fovRange * math.cos(angle),
                                  position_center[1] + self.fovRange * math.sin(angle)
                                )

            # collisions center_rectangle
            collisions_beam = pg.space.segment_query(position_center, position_end_cone, self.radius_beam, self.filter)

            # left
            angle = self.anchor.pm_body.angle + l_angle
            position_end_segment = (position_center[0] + self.fovRange * math.cos(angle),
                                    position_center[1] + self.fovRange * math.sin(angle)
                                    )

            position_start = (position_center[0] + self.radius_beam / 4 * math.cos(math.pi / 2 + angle),
                              position_center[1] + self.radius_beam / 4 * math.sin(math.pi / 2 + angle)
                              )
            position_end_rect = (position_end_segment[0] + self.radius_beam / 4 * math.cos(math.pi / 2 + angle),
                                 position_end_segment[1] + self.radius_beam / 4 * math.sin(math.pi / 2 + angle)
                                 )

            collisions_l_segm = pg.space.segment_query(position_center, position_end_segment, 1, self.filter)
            collisions_l_rect = pg.space.segment_query(position_start, position_end_rect, self.radius_beam / 2,
                                                       self.filter)


            # Right
            angle = self.anchor.pm_body.angle + r_angle
            position_end_segment = (position_center[0] + self.fovRange * math.cos(angle),
                                    position_center[1] + self.fovRange * math.sin(angle)
                                    )

            position_start = (position_center[0] + self.radius_beam / 4 * math.cos(-math.pi / 2 + angle),
                              position_center[1] + self.radius_beam / 4 * math.sin(-math.pi / 2 + angle)
                              )
            position_end_rect = (position_end_segment[0] + self.radius_beam / 4 * math.cos(-math.pi / 2 + angle),
                                 position_end_segment[1] + self.radius_beam / 4 * math.sin(-math.pi / 2 + angle)
                                 )



            collisions_r_segm = pg.space.segment_query(position_center, position_end_segment, 1, self.filter)
            collisions_r_rect = pg.space.segment_query(position_start, position_end_rect, self.radius_beam / 2,
                                                       self.filter)

            collisions_r_segm_shapes = [col.shape for col in collisions_r_segm]
            collisions_r_rect_shapes = [col.shape for col in collisions_r_rect]
            collisions_l_segm_shapes = [col.shape for col in collisions_l_segm]
            collisions_l_rect_shapes = [col.shape for col in collisions_l_rect]

            filtered_collisions = [col for col in collisions_beam if
                                   col.shape not in collisions_r_rect_shapes
                                   or (col.shape in collisions_r_rect_shapes and col.shape in collisions_r_segm_shapes)
                                   ]

            filtered_collisions = [col for col in filtered_collisions if
                                   col.shape not in collisions_l_rect_shapes
                                   or (col.shape in collisions_l_rect_shapes and col.shape in collisions_l_segm_shapes)
                                   ]

            collisions = filtered_collisions

            shapes = [collision.shape for collision in collisions]
            distances = [collision.alpha * self.fovRange for collision in collisions]

            entities_dist = [(pg.get_scene_element_from_shape(shape), dist)
                             for shape, dist in zip(shapes, distances)
                             if shape.sensor == False]

            entities = list(set([ LidarPoint(ent, dist, cone_angle) for ent, dist in entities_dist
                                  if ent is not None and ent.pm_visible_shape is not None]))

            agents = [pg.get_agent_from_shape(shape) for shape in shapes]
            agents = [LidarPoint(ag, dist, cone_angle) for ag, dist in zip(agents, distances) if ag is not None]
            agents = list(set([ pt for pt in agents if (len(set(pt.entity.body_parts) & set(self.invisible_elements)) == 0)]))

            self.sensor_value[cone_angle] = entities + agents

        self.filter_sensor_values()

    @property
    def shape(self):
        return None
#
#
#
# class LidarOcclusion(Lidar):
#
#     def __init__(self, anchor, invisible_elements, **sensor_params):
#
#         super().__init__(anchor, invisible_elements, **sensor_params)
#
#     def update_sensor(self, pg):
#
#         super().update_sensor(pg)
#
#         for angle, points in self.sensor_value.items():
#
#
#             if points != []:
#                 min_distance_point = min( points, key=attrgetter('distance') )
#                 self.sensor_value[angle] = [min_distance_point]
#
#             else:
#                 self.sensor_value[angle] = []
#
#
# class LidarOcclusionUnique(LidarOcclusion):
#
#     def __init__(self, anchor, invisible_elements, **sensor_params):
#
#         super().__init__(anchor, invisible_elements, **sensor_params)
#
#     def update_sensor(self, pg):
#
#         super().update_sensor(pg)
#
#         unique_points = {}
#
#         all_points = []
#
#         for angle, points in self.sensor_value.items():
#             all_points += points
#
#         for point in all_points:
#
#             min_distance_point = min( [ pt for pt in all_points if pt.entity is point.entity], key=attrgetter('distance') )
#
#             unique_points[min_distance_point.angle] = [min_distance_point]
#
#         self.sensor_value = unique_points
