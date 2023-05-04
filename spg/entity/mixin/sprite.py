from typing import Optional, Tuple

import numpy as np
import pymunk
from PIL import Image
from arcade import Sprite, Texture
from skimage.draw import disk, polygon

from spg.definitions import INVISIBLE_ALPHA


class SpriteMixin:

    uid: int

    def __init__(
        self,
        filename: Optional[str] = None,
        texture: Optional[Texture] = None,
        radius: Optional[float] = None,
        width: Optional[float] = None,
        height: Optional[float] = None,
        sprite_front_is_up: bool = False,
        color: Optional[Tuple[int, int, int]] = None,
        transparency: Optional[float] = None,
        **_,
    ):

        assert texture is not None or filename is not None

        # Get the base sprite
        self.sprite = Sprite(
            texture=texture,
            filename=filename,
            hit_box_algorithm="Detailed",
            hit_box_detail=1,
            flipped_diagonally=sprite_front_is_up,
            flipped_horizontally=sprite_front_is_up,
        )  # type: ignore

        self.color = color

        # Get the scale and dimensions
        self.scale, self.radius, self.width, self.height = self._get_dimensions(
            radius, width, height
        )

        self._transparency = transparency

    @property
    def texture(self):
        return self.sprite.texture

    @property
    def color_uid(self):
        return self.uid & 255, (self.uid >> 8) & 255, (self.uid >> 16) & 255, 255

    ##############
    # Init pm Elements
    ###############
    def _get_dimensions(self, radius, width, height):

        orig_radius = max(
            pymunk.Vec2d(*vert).length for vert in self.sprite.get_hit_box()
        )

        horiz = [pymunk.Vec2d(*vert).x for vert in self.sprite.get_hit_box()]
        vert = [pymunk.Vec2d(*vert).y for vert in self.sprite.get_hit_box()]

        orig_width = max(horiz) - min(horiz)
        orig_height = max(vert) - min(vert)

        # If radius imposed:
        if radius:
            scale = radius / orig_radius

        elif height:
            scale = height / orig_height

        elif width:
            scale = width / orig_width
        else:
            scale = 1

        width = scale * orig_width
        height = scale * orig_height
        radius = scale * orig_radius

        return scale, radius, width, height

    ##############
    # Sprites
    ##############

    def get_sprite(self, zoom: float = 1, color_uid=False) -> Sprite:

        texture = self.sprite.texture
        if color_uid:
            texture = self.color_with_id(texture)

        assert isinstance(texture, Texture)

        sprite = Sprite(
            texture=texture,
            scale=zoom * self.scale,
            hit_box_algorithm="Detailed",
            hit_box_detail=1,
        )

        if self.color and not color_uid:
            sprite.color = self.color

        if self._transparency:
            sprite.alpha = INVISIBLE_ALPHA

        return sprite

    def color_with_id(self, texture) -> Texture:

        img_uid = Image.new("RGBA", texture.size)
        pixels = img_uid.load()
        pixels_texture = texture.image.load()

        for i in range(img_uid.size[0]):
            for j in range(img_uid.size[1]):

                if pixels_texture[i, j][3] == 0:
                    pixels[i, j] = (0, 0, 0, 0)

                elif pixels_texture[i, j][:3] != (0, 0, 0):  # type: ignore
                    pixels[i, j] = self.color_uid  # type: ignore

                else:
                    pixels[i, j] = (0, 0, 0, 0)

        texture = Texture(
            name=str(self.uid),
            image=img_uid,
            hit_box_algorithm="Detailed",
            hit_box_detail=1,
        )

        return texture


def get_texture_from_shape(pm_shape, color, name_texture):

    color_rgba = list(color) + [255]

    if isinstance(pm_shape, pymunk.Segment):
        radius = int(pm_shape.radius)
        length = int((pm_shape.a - pm_shape.b).length)
        img = np.zeros((radius, length, 4))
        img[:, :] = color_rgba

    elif isinstance(pm_shape, pymunk.Circle):
        radius = int(pm_shape.radius)

        img = np.zeros((2 * radius + 1, 2 * radius + 1, 4))
        rr, cc = disk((radius, radius), radius)
        img[rr, cc] = color_rgba

    elif isinstance(pm_shape, pymunk.Poly):
        vertices = pm_shape.get_vertices()

        top = max(vert[0] for vert in vertices)
        bottom = min(vert[0] for vert in vertices)
        left = min(vert[1] for vert in vertices)
        right = max(vert[1] for vert in vertices)

        w = int(right - left)
        h = int(top - bottom)

        center = int(h / 2), int(w / 2)

        img = np.zeros((h, w, 4))
        r = [y + center[0] for x, y in vertices]
        c = [x + center[1] for x, y in vertices]

        rr, cc = polygon(r, c, (h, w))

        img[rr, cc] = color_rgba

    else:
        raise ValueError

    PIL_image = Image.fromarray(np.uint8(img)).convert("RGBA")

    texture = Texture(
        name=name_texture,
        image=PIL_image,
        hit_box_algorithm="Detailed",
        hit_box_detail=1,
    )

    return texture
