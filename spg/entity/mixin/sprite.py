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
                    pixels[i, j] = (0, 0, 0, 0)  # type: ignore

                elif pixels_texture[i, j][:3] != (0, 0, 0):
                    pixels[i, j] = self.color_uid  # type: ignore

                else:
                    pixels[i, j] = (0, 0, 0, 0)  # type: ignore

        texture = Texture(
            name=str(self.uid),
            image=img_uid,
            hit_box_algorithm="Detailed",
            hit_box_detail=1,
        )

        return texture


def get_texture_from_geometry(geometry: str,
                              radius: Optional[int] = None,
                              size: Optional[Tuple[int, int]] = None,
                              vertices: Optional[np.ndarray] = None,
                              color: Optional[Tuple[int, int, int]] = None,
                              name_texture: Optional[str] = None,
                              **_: object,
                              ) -> object:
    color_rgba = list(color) + [255]

    offset = 0, 0

    if geometry == "rectangle":
        assert size is not None, "Size must be provided for rectangle"
        assert len(size) == 2, "Size must be a tuple of length 2"
        img = np.zeros((*size, 4), dtype=np.uint8)
        img[:, :] = color_rgba

    elif geometry == "circle":
        assert radius is not None, "Radius must be provided for circle"
        img = np.zeros((2 * radius + 1, 2 * radius + 1, 4))
        rr, cc = disk((radius, radius), radius)
        img[rr, cc] = color_rgba

    elif geometry == "polygon":
        assert vertices is not None, "Vertices must be provided for polygon"
        assert vertices.ndim == 2, "Vertices must be a 2D array"
        assert vertices.shape[1] == 2, "Vertices must have 2 columns (x, y)"

        bottom, left = np.min(vertices, axis=0)
        top, right = np.max(vertices, axis=0)

        r = [y - left for x, y in vertices]
        c = [x - bottom for x, y in vertices]

        rr, cc = polygon(c, r)

        # create image based on rr, cc
        img = np.zeros((int(np.max(rr))+1, int(np.max(cc))+1, 4))
        img[rr, cc] = color_rgba

        # rotate image by 90 degrees
        img = np.rot90(img, k=1)

        center = (top - bottom) // 2, (right - left) // 2

        offset = int(bottom) + center[0], int(left) + center[1]

    else:
        raise ValueError(f"Invalid shape: {geometry}")

    PIL_image = Image.fromarray(np.uint8(img))
    texture = Texture(
        name=name_texture,
        image=PIL_image,
        hit_box_algorithm="Detailed",
        hit_box_detail=1,
    )

    return texture, offset
