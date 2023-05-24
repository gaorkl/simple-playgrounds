from typing import List, Optional, Tuple, Union

from arcade import Window

from spg.core.view import View


class ViewManager:
    def __init__(
        self,
        background: Optional[
            Union[Tuple[int, int, int], List[int], Tuple[int, int, int, int]]
        ] = None,
        **_
    ):

        if not background:
            background = (0, 0, 0, 255)

        if len(background) == 3:
            background = (*background, 255)

        self.background = background

        self.views: List[View] = []

        self._window = Window(1, 1, visible=False, antialiasing=False)  # type: ignore

    @property
    def ctx(self):
        return self._window.ctx

    @property
    def window(self):
        return self._window

    def add_view(self, view):

        if view in self.views:
            raise ValueError("View already added")

        self.views.append(view)

        for element in self.elements:
            view.add(element)

        for agent in self.agents:
            view.add(agent)

    def remove_view(self, view):
        self.views.remove(view)

    # @property
    # def ray_compute(self):

    #     if not self._ray_compute:
    #         assert self._size
    #         self._ray_compute = RayCompute(
    #             self, self._size, self._center, zoom=1, use_shader=self._use_shaders
    #         )

    #     return self._ray_compute

    # if self._ray_compute:
    #     self._ray_compute.update_sensors()

    # def add_view(self, view):
    #
    #     for entity in self.elements:
    #         view.add(entity)
    #
    #         if isinstance(entity, PhysicalElement):
    #             for interactive in entity.interactives:
    #                 view.add(interactive)
    #
    #     for agents in self.agents:
    #         for part in agents.parts:
    #             view.add(part)
    #
    #             for device in part.devices:
    #                 view.add(device)
    #
    #     self._views.append(view)
