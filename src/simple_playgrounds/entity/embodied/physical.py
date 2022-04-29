from __future__ import annotations
from abc import ABC
from typing import Optional, List, TYPE_CHECKING
import pymunk


from simple_playgrounds.entity.embodied.interactive import AnchoredInteractive

if TYPE_CHECKING:
    from simple_playgrounds.playground.playground import Playground
    from simple_playgrounds.common.position_utils import InitCoord

from simple_playgrounds.common.definitions import PymunkCollisionCategories

from simple_playgrounds.entity.embodied.embodied import EmbodiedEntity


class PhysicalEntity(EmbodiedEntity, ABC):
    """
    PhysicalEntity creates a physical object that can collide with other Physical Entities.
    It deals with physical properties such as the mass, visual texture, whether it is transparent or traversable.
    PhysicalEntity is visible and non-traversable by default.
    An agent is composed of multiple PhysicalEntity that are attached to each other.
    """

    def __init__(
            self,
            playground: Playground,
            initial_coordinates: InitCoord,
            mass: Optional[float] = None,
            traversable: bool = False,
            transparent: bool = False,
            **kwargs,
    ):

        self._mass = mass
        self._transparent = transparent
        self._traversable = traversable
        
        super().__init__(playground=playground, initial_coordinates=initial_coordinates, **kwargs)
        
        self._set_shape_collision_filter()
        self.update_team_filter()

        self._interactives: List[AnchoredInteractive] = []
    
    @property
    def transparent(self):
        return self._transparent

    @property
    def traversable(self):
        return self._traversable

    ########################
    # BODY AND SHAPE
    ########################

    def _get_pm_body(self):

        if not self._mass:
            return pymunk.Body(body_type=pymunk.Body.STATIC)

        vertices = self._base_sprite.get_hit_box()
        moment = pymunk.moment_for_poly(self._mass, vertices)

        return pymunk.Body(self._mass, moment, body_type= pymunk.Body.DYNAMIC)

    def _set_shape_collision_filter(self):

        # By default, a physical entity collides with all
        if self._transparent and self._traversable:
            raise ValueError('Physical Entity can not be transparent and traversable. Use Interactive Entity.')

        categories = 2 ** PymunkCollisionCategories.NO_TEAM.value
        mask = pymunk.ShapeFilter.ALL_MASKS() ^ 2 ** PymunkCollisionCategories.TRAVERSABLE.value

        # If traversable, collides with nothing
        if self._traversable:
            categories = 2 ** PymunkCollisionCategories.TRAVERSABLE.value
            mask = 0

        # If transparent, collides with everything except tra.
        # if self._transparent:
        #     categories = 2 ** PymunkCollisionCategories.TRANSPARENT.value

        self._pm_shape.filter = pymunk.ShapeFilter(categories=categories, mask=mask)


    ###################
    # Iteractions with Playground
    ###################

    def add_interactive(self, interactive):
        self._interactives.append(interactive)

    def pre_step(self):
        """
        Performs calculation before the physical environment steps.
        """
        for interactive in self._interactives:
            interactive.pre_step()

    def post_step(self, **kwargs):
        for interactive in self._interactives:
            interactive.post_step(**kwargs)

    def remove(self, **kwargs):
        super().remove(**kwargs)
        for interactive in self._interactives:
            interactive.remove(**kwargs)

    def reset(self, **kwargs):
        super().reset()
        for interactive in self._interactives:
            interactive.reset(**kwargs)
