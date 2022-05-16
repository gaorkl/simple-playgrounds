import numpy as np
from skimage import draw, morphology
from PIL import Image
import pymunk

from arcade.texture import Texture

from simple_playgrounds.common.definitions import CollisionTypes, PymunkCollisionCategories
from simple_playgrounds.entity.embodied.interactive import AnchoredInteractive, StandAloneInteractive
from simple_playgrounds.entity.embodied.physical import PhysicalEntity
from simple_playgrounds.entity.entity import Entity
from simple_playgrounds.playground.collision_handlers import get_colliding_entities
from simple_playgrounds.entity.embodied.embodied import EmbodiedEntity


class MockPhysicalMovable(PhysicalEntity):

    def __init__(self, playground, initial_coordinates, radius = None, **kwargs):

        super().__init__(playground, initial_coordinates, mass=10, radius = radius,
                         filename=":resources:onscreen_controls/flat_light/play.png", **kwargs)
        
    def _set_pm_collision_type(self):
        pass


class MockPhysicalUnmovable(PhysicalEntity):

    def __init__(self, playground, initial_coordinates, radius = None, **kwargs):

        super().__init__(playground, initial_coordinates, radius = radius,
                         filename=":resources:onscreen_controls/flat_light/close.png", **kwargs)
        
    def _set_pm_collision_type(self):
        pass


class MockPhysicalFromShape(PhysicalEntity):

    def __init__(self, playground, initial_coordinates, geometry, size, mass = None, **kwargs):

        if geometry == 'segment':
            pm_shape = pymunk.Segment(None, (-size, 0), (size, 0), radius=1)
        elif geometry == 'circle':
            pm_shape = pymunk.Circle(None, size)
        elif geometry == 'square':
            pm_shape = pymunk.Poly(None, ((-size, -size), (-size, size), (size, size), (size, -size)))
        else:
            raise ValueError

        super().__init__(playground, initial_coordinates, mass, pm_shape=pm_shape, **kwargs)


    def _set_pm_collision_type(self):
        pass

class MockHalo(AnchoredInteractive):
    
    def __init__(self, anchor: PhysicalEntity, interaction_range, trigger, triggered):

        self._trigger = trigger
        self._triggered = triggered

        super().__init__(anchor, interaction_range)

    def _set_pm_collision_type(self):
        
        if self._trigger:
            for pm_shape in self._pm_shapes:
                pm_shape.collision_type = CollisionTypes.TEST_TRIGGER

        elif self._triggered:
            for pm_shape in self._pm_shapes:
                pm_shape.collision_type = CollisionTypes.TEST_TRIGGERED

    def trigger(self):
        self._activated = True


class MockPhysicalInteractive(PhysicalEntity):
    
    def __init__(self, playground, initial_coordinates, interaction_range, radius = None, trigger = False, triggered=False, **kwargs):

        super().__init__(playground, initial_coordinates, radius = radius, mass=10,
                         filename=":resources:onscreen_controls/flat_light/star_round.png", **kwargs)
       
        self.halo = MockHalo(self, interaction_range=interaction_range, trigger=trigger, triggered = triggered)

    def _set_pm_collision_type(self):
        pass


class MockPhysicalTrigger(MockPhysicalMovable):

    def __init__(self, playground, initial_coordinates, radius=None, **kwargs):
        
        self._activated = False   
        super().__init__(playground, initial_coordinates, radius, **kwargs)

    def _set_pm_collision_type(self):
        for pm_shape in self._pm_shapes:
            pm_shape.collision_type = CollisionTypes.TEST_TRIGGER

    def trigger(self):
        self._activated = True


    def pre_step(self):
        self._activated = False
        return super().pre_step()


class MockZoneInteractive(StandAloneInteractive):

    def __init__(self, playground, initial_coordinates, radius = None, trigger = False, triggered=False, **kwargs):
 
        self._trigger = trigger
        self._triggered = triggered

        super().__init__(playground, initial_coordinates, radius = radius,
                         filename=":resources:onscreen_controls/flat_light/star_square.png", **kwargs)

    def _set_pm_collision_type(self):

        if self._trigger:
            for pm_shape in self._pm_shapes:
                pm_shape.collision_type = CollisionTypes.TEST_TRIGGER

        elif self._triggered:
            for pm_shape in self._pm_shapes:
                pm_shape.collision_type = CollisionTypes.TEST_TRIGGERED

    def trigger(self):
        self._activated = True


class NonConvexPlus_Approx(MockPhysicalMovable):

    def __init__(self, playground, initial_coordinates, radius, width, **kwargs):
        
        img = np.zeros((2*radius+2*width+1,2*radius+2*width+1, 4))
       
        rr, cc = draw.line(width, radius + width, width + 2*radius, radius + width)
        img[rr, cc, :] = 1

        rr, cc = draw.line(radius + width, width, radius + width, width + 2*radius)
        img[rr, cc, :] = 1

        for _ in range(int(width/2)-1):
            img = morphology.binary_dilation(img)

        PIL_image = Image.fromarray(np.uint8(img*255)).convert('RGBA')

        texture = Texture(name="PLus_%i_%i".format(radius, int), image=PIL_image, hit_box_algorithm='Detailed', hit_box_detail=2)

        super().__init__(playground, initial_coordinates, texture=texture, **kwargs)



class NonConvexPlus(MockPhysicalMovable):

    def __init__(self, playground, initial_coordinates, radius, width):
        
        img = np.zeros((2*radius+2*width+1,2*radius+2*width+1, 4))
       
        rr, cc = draw.line(width, radius + width, width + 2*radius, radius + width)
        img[rr, cc, :] = 1

        rr, cc = draw.line(radius + width, width, radius + width, width + 2*radius)
        img[rr, cc, :] = 1

        for _ in range(int(width/2)-1):
            img = morphology.binary_dilation(img)

        PIL_image = Image.fromarray(np.uint8(img*255)).convert('RGBA')

        texture = Texture(name="PLus_%i_%i".format(radius, int), image=PIL_image, hit_box_algorithm='Detailed', hit_box_detail=2)

        super().__init__(playground, initial_coordinates, texture=texture, shape_approximation='decomposition')

class NonConvexC(MockPhysicalMovable):

    def __init__(self, playground, initial_coordinates, radius, width):
        
        img = np.zeros((2*radius+2*width+1,2*radius+2*width+1, 4))
       
        rr, cc = draw.circle_perimeter(radius + width, radius+width, radius )
        img[rr, cc, :] = 1

        rr, cc = draw.polygon((0, 0, radius+width), (0, 2*radius + 2*width, radius+width))
        img[rr, cc, :] = 0

        for _ in range(int(width/2)-1):
            img = morphology.binary_dilation(img)

        PIL_image = Image.fromarray(np.uint8(img*255)).convert('RGBA')

        texture = Texture(name="C_%i_%i".format(radius, width), image=PIL_image, hit_box_algorithm='Detailed', hit_box_detail=4)

        super().__init__(playground, initial_coordinates, texture=texture, shape_approximation='decomposition')


class MockBarrier(MockPhysicalUnmovable):

    def __init__(self, playground, begin_pt, end_pt, width, **kwargs):
  
        self.width = width
        self._length_barrier = (pymunk.Vec2d(*begin_pt) - end_pt).length
        position = (pymunk.Vec2d(*begin_pt) + end_pt)/2
        orientation = (pymunk.Vec2d(*end_pt) - begin_pt).angle

        img = np.ones( (int(self._length_barrier), width, 4))
        PIL_image = Image.fromarray(np.uint8(img*255)).convert('RGBA')

        texture = Texture(name="Barrier_%i_%i".format(int(self._length_barrier), width), image=PIL_image, hit_box_algorithm='Detailed', hit_box_detail=1)

        super().__init__(playground, (position, orientation), texture=texture, **kwargs)

    def _get_pm_shapes(self, *_):
        return [pymunk.Segment(self._pm_body, (-self._length_barrier/2, 0), (self._length_barrier/2, 0), self.width)]

    def update_team_filter(self):

        # if not self._teams:
        #     return

        categ = 2 ** PymunkCollisionCategories.NO_TEAM.value
        for team in self._teams:
            categ = categ | 2 ** self._playground.teams[team]

        mask = 0
        for team in self._playground.teams:

            if team not in self._teams:
                mask = mask | 2 ** self._playground.teams[team]

        for pm_shape in self.pm_shapes:
            pm_shape.filter = pymunk.ShapeFilter(categories=categ, mask=mask)





def trigger_triggers_triggered(arbiter, space, data):

    playground = data['playground']
    (trigger, _), (triggered, _) = get_colliding_entities(playground, arbiter)

    if not trigger.teams and triggered.teams:
        return True

    trigger.trigger()
    triggered.trigger()

    return True


# class MockPhysical(PhysicalEntity):

#     def __init__(self, pg, coord, **kwargs):
#         super().__init__(playground=pg, initial_coordinates=coord, appearance=ColorTexture(color=(121, 10, 220)), **kwargs)

#     def post_step(self):
#         pass

#     def _set_pm_collision_type(self):
#         pass

# class MockHaloTrigger(AnchoredInteractive):

#     def __init__(self, anchor, **kwargs):
#         super().__init__(anchor=anchor, appearance=ColorTexture(color=(121, 10, 220)), **kwargs)
#         self.activated = False

#     def pre_step(self):
#         self.activated = False

#     def post_step(self):
#         pass

#     def _set_pm_collision_type(self):
#         self._pm_shape.collision_type = CollisionTypes.TEST_TRIGGER

#     def trigger(self):
#         self.activated = True


# class MockHaloTriggered(MockHaloTrigger):

#     def _set_pm_collision_type(self):
#         self._pm_shape.collision_type = CollisionTypes.TEST_TRIGGERED


# class MockZoneTrigger(StandAloneInteractive):

#     def __init__(self, pg, coord, **kwargs):
#         super().__init__(playground=pg, initial_coordinates=coord, appearance=ColorTexture(color=(121, 10, 220)), **kwargs)
#         self.activated = False

#     def _set_pm_collision_type(self):
#         self._pm_shape.collision_type = CollisionTypes.TEST_TRIGGER

#     def pre_step(self):
#         self.activated = False

#     def post_step(self):
#         pass

#     def trigger(self):
#         self.activated = True


# class MockZoneTriggered(MockZoneTrigger):

#     def _set_pm_collision_type(self):
#         self._pm_shape.collision_type = CollisionTypes.TEST_TRIGGERED


# class MockBarrier(PhysicalEntity):

#     def __init__(self, pg, coord, **kwargs):
#         super().__init__(playground=pg, initial_coordinates=coord, appearance=ColorTexture(color=(121, 10, 220)), **kwargs)

#     def update_team_filter(self):

#         # if not self._teams:
#         #     return

#         categ = 2 ** PymunkCollisionCategories.NO_TEAM.value
#         for team in self._teams:
#             categ = categ | 2 ** self._playground.teams[team]

#         mask = 0
#         for team in self._playground.teams:

#             if team not in self._teams:
#                 mask = mask | 2 ** self._playground.teams[team]

#         self._pm_shape.filter = pymunk.ShapeFilter(categories=categ, mask=mask)


#     def post_step(self):
#         pass

#     def _set_pm_collision_type(self):
#         pass


