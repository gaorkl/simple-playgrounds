import numpy as np
import pymunk
from arcade.texture import Texture
from PIL import Image
from skimage import draw, morphology

from spg.element import ColorWall, PhysicalElement, ZoneElement
from spg.entity import InteractiveAnchored
from spg.playground import get_colliding_entities
from spg.utils.definitions import CollisionTypes, PymunkCollisionCategories
from spg.utils.sprite import get_texture_from_shape


class MockPhysicalFromResource(PhysicalElement):
    def __init__(self, filename, **kwargs):
        super().__init__(mass=10, filename=filename, **kwargs)

    @property
    def _collision_type(self):
        return CollisionTypes.ELEMENT


class MockPhysicalMovable(PhysicalElement):
    def __init__(self, radius=None, **kwargs):

        super().__init__(
            mass=10,
            radius=radius,
            filename=":resources:onscreen_controls/flat_light/play.png",
            **kwargs,
        )

    @property
    def _collision_type(self):
        return CollisionTypes.ELEMENT


class MockPhysicalUnmovable(PhysicalElement):
    def __init__(self, radius=None, **kwargs):

        super().__init__(
            radius=radius,
            filename=":resources:onscreen_controls/flat_light/close.png",
            **kwargs,
        )

    @property
    def _collision_type(self):
        return CollisionTypes.ELEMENT


class MockPhysicalFromShape(PhysicalElement):
    def __init__(self, geometry, size, color, mass=None, **kwargs):

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

        texture = get_texture_from_shape(pm_shape, color, "geometry_" + str(size))

        super().__init__(mass=mass, texture=texture, **kwargs)

    @property
    def _collision_type(self):
        return CollisionTypes.ELEMENT


class MockHalo(InteractiveAnchored):
    def __init__(self, anchor: PhysicalElement, interaction_range):
        super().__init__(anchor, interaction_range)
        self._activated = False

    @property
    def _collision_type(self):
        return CollisionTypes.PASSIVE_INTERACTOR

    def pre_step(self):
        self._activated = False

    def activate(self):
        self._activated = True

    @property
    def activated(self):
        return self._activated


class MockPhysicalInteractive(PhysicalElement):
    def __init__(self, interaction_range, radius=None, **kwargs):

        super().__init__(
            radius=radius,
            mass=10,
            filename=":resources:onscreen_controls/flat_light/star_round.png",
            **kwargs,
        )

        self.halo = MockHalo(
            self,
            interaction_range=interaction_range,
        )
        self.add(self.halo)

    @property
    def _collision_type(self):
        return CollisionTypes.ELEMENT


class MockZoneInteractive(ZoneElement):
    def __init__(self, radius=None, **kwargs):
        super().__init__(
            radius=radius,
            filename=":resources:onscreen_controls/flat_light/star_square.png",
            **kwargs,
        )
        self._activated = False

    @property
    def _collision_type(self):
        return CollisionTypes.PASSIVE_INTERACTOR

    def pre_step(self):
        self._activated = False

    def activate(self):
        self._activated = True

    @property
    def activated(self):
        return self._activated


class NonConvexPlus_Approx(MockPhysicalMovable):
    def __init__(self, radius, width, **kwargs):

        img = np.zeros((2 * radius + 2 * width + 1, 2 * radius + 2 * width + 1, 4))

        rr, cc = draw.line(width, radius + width, width + 2 * radius, radius + width)
        img[rr, cc, :] = 1

        rr, cc = draw.line(radius + width, width, radius + width, width + 2 * radius)
        img[rr, cc, :] = 1

        for _ in range(int(width / 2) - 1):
            img = morphology.binary_dilation(img)

        PIL_image = Image.fromarray(np.uint8(img * 255)).convert("RGBA")

        texture = Texture(
            name=f"PLus_{radius}_{width}",
            image=PIL_image,
            hit_box_algorithm="Detailed",
            hit_box_detail=2,
        )

        super().__init__(texture=texture, **kwargs)

    @property
    def _collision_type(self):
        return CollisionTypes.ELEMENT


class NonConvexPlus(MockPhysicalMovable):
    def __init__(
        self,
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
            name=f"PLus_{radius}_{width}",
            image=PIL_image,
            hit_box_algorithm="Detailed",
            hit_box_detail=1,
        )

        super().__init__(
            texture=texture,
            shape_approximation=shape_approximation,
        )

    @property
    def _collision_type(self):
        return CollisionTypes.ELEMENT


class NonConvexC(MockPhysicalMovable):
    def __init__(
        self,
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
            name=f"C_{radius}_{width}",
            image=PIL_image,
            hit_box_algorithm="Detailed",
            hit_box_detail=1,
        )

        super().__init__(
            texture=texture,
            shape_approximation=shape_approximation,
        )

    @property
    def _collision_type(self):
        return CollisionTypes.ELEMENT


class MockBarrier(ColorWall):
    def __init__(self, begin_pt, end_pt, width, **kwargs):

        super().__init__(begin_pt, end_pt, width=width, color=(0, 10, 2), **kwargs)

    def update_team_filter(self):

        assert self._playground

        categ = 2**PymunkCollisionCategories.NO_TEAM.value
        for team in self._teams:
            categ = categ | 2 ** self._playground.teams[team]

        mask = 0
        for team_name, team_id in self._playground.teams.items():
            if team_name not in self._teams:
                mask = mask | 2**team_id

        for pm_shape in self.pm_shapes:
            pm_shape.filter = pymunk.ShapeFilter(categories=categ, mask=mask)


def active_interaction(arbiter, _, data):

    playground = data["playground"]
    (activator, _), (activated, _) = get_colliding_entities(playground, arbiter)

    if activator.activated:
        activated.activate()

    return True


def passive_interaction(arbiter, _, data):

    playground = data["playground"]
    (activated_1, _), (activated_2, _) = get_colliding_entities(playground, arbiter)

    activated_1.activate()
    activated_2.activate()

    return True
