import numpy as np
from skimage import draw, morphology
from PIL import Image
import pymunk

from arcade.texture import Texture

from simple_playgrounds.common.definitions import (
    CollisionTypes,
    PymunkCollisionCategories,
)
from simple_playgrounds.element.basic.wall import ColorWall
from simple_playgrounds.entity.interactive import (
    AnchoredInteractive,
    StandAloneInteractive,
)
from simple_playgrounds.entity.physical import PhysicalEntity
from simple_playgrounds.playground.collision_handlers import get_colliding_entities


class MockPhysicalFromResource(PhysicalEntity):
    def __init__(self, playground, initial_coordinates, filename, **kwargs):

        super().__init__(
            playground, initial_coordinates, mass=10, filename=filename, **kwargs
        )

    def _set_pm_collision_type(self):
        pass


class MockPhysicalMovable(PhysicalEntity):
    def __init__(self, playground, initial_coordinates, radius=None, **kwargs):

        super().__init__(
            playground,
            initial_coordinates,
            mass=10,
            radius=radius,
            filename=":resources:onscreen_controls/flat_light/play.png",
            **kwargs
        )

    def _set_pm_collision_type(self):
        pass


class MockPhysicalUnmovable(PhysicalEntity):
    def __init__(self, playground, initial_coordinates, radius=None, **kwargs):

        super().__init__(
            playground,
            initial_coordinates,
            radius=radius,
            filename=":resources:onscreen_controls/flat_light/close.png",
            **kwargs
        )

    def _set_pm_collision_type(self):
        pass


class MockPhysicalFromShape(PhysicalEntity):
    def __init__(
        self, playground, initial_coordinates, geometry, size, mass=None, **kwargs
    ):

        if geometry == "segment":
            pm_shape = pymunk.Segment(None, (-size, 0), (size, 0), radius=5)
        elif geometry == "circle":
            pm_shape = pymunk.Circle(None, size)
        elif geometry == "square":
            pm_shape = pymunk.Poly(
                None, ((-size, -size), (-size, size), (size, size), (size, -size))
            )
        else:
            raise ValueError

        super().__init__(
            playground, initial_coordinates, mass, pm_shape=pm_shape, **kwargs
        )

    def _set_pm_collision_type(self):
        pass


class MockHalo(AnchoredInteractive):
    def __init__(self, anchor: PhysicalEntity, interaction_range):
        super().__init__(anchor, interaction_range)

    def _set_pm_collision_type(self):
        for pm_shape in self._pm_shapes:
            pm_shape.collision_type = CollisionTypes.PASSIVE_INTERACTOR

    def activate(self):
        super().activate()


class MockPhysicalInteractive(PhysicalEntity):
    def __init__(
        self, playground, initial_coordinates, interaction_range, radius=None, **kwargs
    ):

        super().__init__(
            playground,
            initial_coordinates,
            radius=radius,
            mass=10,
            filename=":resources:onscreen_controls/flat_light/star_round.png",
            **kwargs
        )

        self.halo = MockHalo(
            self,
            interaction_range=interaction_range,
        )

    def _set_pm_collision_type(self):
        pass


class MockZoneInteractive(StandAloneInteractive):
    def __init__(self, playground, initial_coordinates, radius=None, **kwargs):
        super().__init__(
            playground,
            initial_coordinates,
            radius=radius,
            filename=":resources:onscreen_controls/flat_light/star_square.png",
            **kwargs
        )

    def _set_pm_collision_type(self):

        for pm_shape in self._pm_shapes:
            pm_shape.collision_type = CollisionTypes.PASSIVE_INTERACTOR

    def activate(self):
        super().activate()


class NonConvexPlus_Approx(MockPhysicalMovable):
    def __init__(self, playground, initial_coordinates, radius, width, **kwargs):

        img = np.zeros((2 * radius + 2 * width + 1, 2 * radius + 2 * width + 1, 4))

        rr, cc = draw.line(width, radius + width, width + 2 * radius, radius + width)
        img[rr, cc, :] = 1

        rr, cc = draw.line(radius + width, width, radius + width, width + 2 * radius)
        img[rr, cc, :] = 1

        for _ in range(int(width / 2) - 1):
            img = morphology.binary_dilation(img)

        PIL_image = Image.fromarray(np.uint8(img * 255)).convert("RGBA")

        texture = Texture(
            name="PLus_%i_%i".format(radius, int),
            image=PIL_image,
            hit_box_algorithm="Detailed",
            hit_box_detail=2,
        )

        super().__init__(playground, initial_coordinates, texture=texture, **kwargs)


class NonConvexPlus(MockPhysicalMovable):
    def __init__(
        self,
        playground,
        initial_coordinates,
        radius,
        width,
        shape_approximation="decomposition",
    ):

        img = np.zeros((2 * radius + 2 * width + 1, 2 * radius + 2 * width + 1, 4))

        rr, cc = draw.line(width, radius + width, width + 2 * radius, radius + width)
        img[rr, cc, :] = 1

        rr, cc = draw.line(radius + width, width, radius + width, width + 2 * radius)
        img[rr, cc, :] = 1

        for _ in range(int(width / 2) - 1):
            img = morphology.binary_dilation(img)

        PIL_image = Image.fromarray(np.uint8(img * 255)).convert("RGBA")

        texture = Texture(
            name="PLus_%i_%i".format(radius, int),
            image=PIL_image,
            hit_box_algorithm="Detailed",
            hit_box_detail=1,
        )

        super().__init__(
            playground,
            initial_coordinates,
            texture=texture,
            shape_approximation=shape_approximation,
        )


class NonConvexC(MockPhysicalMovable):
    def __init__(
        self,
        playground,
        initial_coordinates,
        radius,
        width,
        shape_approximation="decomposition",
    ):
        img = np.zeros((2 * radius + 2 * width + 1, 2 * radius + 2 * width + 1, 4))

        rr, cc = draw.circle_perimeter(radius + width, radius + width, radius)
        img[rr, cc, :] = 1

        rr, cc = draw.polygon(
            (0, 0, radius + width), (0, 2 * radius + 2 * width, radius + width)
        )
        img[rr, cc, :] = 0

        for _ in range(int(width / 2) - 1):
            img = morphology.binary_dilation(img)

        PIL_image = Image.fromarray(np.uint8(img * 255)).convert("RGBA")

        texture = Texture(
            name="C_%i_%i".format(radius, width),
            image=PIL_image,
            hit_box_algorithm="Detailed",
            hit_box_detail=1,
        )

        super().__init__(
            playground,
            initial_coordinates,
            texture=texture,
            shape_approximation=shape_approximation,
        )


class MockBarrier(ColorWall):
    def __init__(self, playground, begin_pt, end_pt, width, **kwargs):

        super().__init__(
            playground, begin_pt, end_pt, width=width, color=(0, 10, 2), **kwargs
        )

    def update_team_filter(self):

        # if not self._teams:
        #     return

        categ = 2**PymunkCollisionCategories.NO_TEAM.value
        for team in self._teams:
            categ = categ | 2 ** self._playground.teams[team]

        mask = 0
        for team in self._playground.teams:

            if team not in self._teams:
                mask = mask | 2 ** self._playground.teams[team]

        for pm_shape in self.pm_shapes:
            pm_shape.filter = pymunk.ShapeFilter(categories=categ, mask=mask)


def active_interaction(arbiter, space, data):

    playground = data["playground"]
    (activator, _), (activated, _) = get_colliding_entities(playground, arbiter)

    if not activator.teams and activated.teams:
        return True

    if activator.activated:
        activated.activate()

    return True


def passive_interaction(arbiter, space, data):

    playground = data["playground"]
    (activated_1, _), (activated_2, _) = get_colliding_entities(playground, arbiter)

    # if (not activated_1.teams and activated_2.teams) or :(not activated_1.teams and activated_2.teams)
    #     return True

    activated_1.activate()
    activated_2.activate()

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
