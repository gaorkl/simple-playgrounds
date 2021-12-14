from __future__ import annotations

from typing import Optional, TYPE_CHECKING
import matplotlib.patches as mpatches
import numpy as np

from simple_playgrounds.common.contour import GeometricShapes
from simple_playgrounds.common.definitions import VISIBLE_ALPHA, INVISIBLE_ALPHA

if TYPE_CHECKING:
    from simple_playgrounds.common.view import View
    from simple_playgrounds.entity.entity import EmbodiedEntity


class Patch():

    def __init__(self,
                 entity: EmbodiedEntity,
                 view: View,
                 **kwargs,
                 ) -> None:

        self._entity = entity
        self._view = view
        self._patch = self._create_patch()
        self._set_alpha(**kwargs)

    def _set_alpha(self, invisible = False, **kwargs):

        if invisible:
            alpha = INVISIBLE_ALPHA
        else:
            alpha = VISIBLE_ALPHA

        self._patch.set_alpha(alpha/255.)
    

    def _create_patch(self):

        contour = self._entity.contour

        if contour.shape == GeometricShapes.CIRCLE:
            assert contour.radius
            patch = mpatches.Circle((0, 0), contour.radius * self._view.zoom, fill=True)

        elif contour.shape == GeometricShapes.POLYGON:
            assert contour.vertices
            vertices = np.asarray(contour.vertices) * self._view.zoom
            patch = mpatches.Polygon(xy=vertices, fill=True)

        else:
            assert contour.radius
            patch = mpatches.RegularPolygon((0, 0),
                                           radius=contour.radius * self._view.zoom,
                                           numVertices=contour.shape.value,
                                           fill=True)
        patch.set_animated(True)
        patch.set_antialiased(False)

        self._view.add_patch(patch)
        return patch

    def update(self):
       
        self._update_patch_position()
        self._update_patch_appearance()

        self._view.draw_patch(self._patch)


    def remove_patch(self):
        self._patch.remove()

    def _update_patch_position(self):

        relative_position = (self._entity.position - self._view.position).rotated(-self._view.angle)

        if self._entity.contour.shape == GeometricShapes.POLYGON:
            vertices = self._entity.contour.get_rotated_vertices(self._entity.angle - self._view.angle)
            vertices = np.asarray(vertices)
            self._patch.set(xy=vertices)

        elif self._entity.contour.shape == GeometricShapes.CIRCLE:
            self._patch.set(center=relative_position)

        else:
            self._patch.xy = relative_position
            self._patch.orientation = self._entity.angle - self._view.angle

    def _update_patch_appearance(self):
        # Should be modified to apply images, textures, only when asked.

        color = [c/255 for c in self._entity.appearance.base_color]
        self._patch.set(color=color)

