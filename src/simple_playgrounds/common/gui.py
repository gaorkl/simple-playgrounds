from __future__ import annotations
from abc import ABC, abstractmethod
from typing import Optional, Tuple, TYPE_CHECKING, Union, Dict
from arcade.sprite import Sprite
from numpy.lib.arraysetops import isin
from simple_playgrounds.agent.part.part import InteractivePart, PhysicalPart
from simple_playgrounds.common.view import TopDownView
from simple_playgrounds.entity.interactive import InteractiveEntity

from simple_playgrounds.entity.physical import PhysicalEntity
from simple_playgrounds.playground.playground import ClosedPlayground


if TYPE_CHECKING:
    from simple_playgrounds.playground.playground import Playground
    from simple_playgrounds.common.position_utils import Coordinate
    from simple_playgrounds.entity.embodied import EmbodiedEntity
    from simple_playgrounds.agent.agents import HeadAgent

import numpy as np
import arcade

import matplotlib.pyplot as plt

from PIL import Image, ImageShow


class GUI(TopDownView):
    def __init__(
        self,
        playground: Playground,
        agent: HeadAgent,
        size: Optional[Tuple[int, int]] = None,
        center: Tuple[float, float] = (0, 0),
        zoom: float = 1,
        display_uid: bool = False,
        draw_transparent: bool = True,
        draw_interactive: bool = True,
    ) -> None:
        super().__init__(
            playground,
            size,
            center,
            zoom,
            display_uid,
            draw_transparent,
            draw_interactive,
        )

        self._playground.set_size(*self._size)
        self._playground.set_visible(True)

        self._playground.gui = self

        self._agent = agent

        self._agent_commands = {}

    @property
    def commands(self):
        return {self._agent: self._agent_commands}

    def update(self, force=False):

        self.update_sprites(force)

        self._playground.use()

        self._playground.clear(self._background)

        # Change projection to match the contents

        self._transparent_sprites.draw(pixelated=True)
        self._interactive_sprites.draw(pixelated=True)
        self._visible_sprites.draw(pixelated=True)
        self._traversable_sprites.draw(pixelated=True)

    def on_key_press(self, key, modifiers):
        """Called whenever a key is pressed."""

        if key == arcade.key.UP:
            self._agent_commands[self._agent.base.forward_controller] = 200
        elif key == arcade.key.DOWN:
            self._agent_commands[self._agent.base.forward_controller] = -200

        if not (modifiers & arcade.key.MOD_SHIFT):
            if key == arcade.key.LEFT:
                self._agent_commands[self._agent.base.angular_vel_controller] = 0.2
            elif key == arcade.key.RIGHT:
                self._agent_commands[self._agent.base.angular_vel_controller] = -0.2
        else:
            if key == arcade.key.LEFT:
                self._agent_commands[self._agent.head.joint_controller] = 0.2
            elif key == arcade.key.RIGHT:
                self._agent_commands[self._agent.head.joint_controller] = -0.2

        if key == arcade.key.Q:
            self._playground.close()

    def on_key_release(self, key, modifiers):

        agent_commands = {}

        if key == arcade.key.UP:
            self._agent_commands[self._agent.base.forward_controller] = 0
        elif key == arcade.key.DOWN:
            self._agent_commands[self._agent.base.forward_controller] = 0
        if not (modifiers & arcade.key.MOD_SHIFT):
            if key == arcade.key.LEFT:
                self._agent_commands[self._agent.base.angular_vel_controller] = 0
            elif key == arcade.key.RIGHT:
                self._agent_commands[self._agent.base.angular_vel_controller] = 0
        else:
            if key == arcade.key.LEFT:
                self._agent_commands[self._agent.head.joint_controller] = 0
            elif key == arcade.key.RIGHT:
                self._agent_commands[self._agent.head.joint_controller] = 0
