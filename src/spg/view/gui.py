from __future__ import annotations

from typing import TYPE_CHECKING, Dict, Optional, Tuple

import arcade

from .view import TopDownView

if TYPE_CHECKING:
    from ..agent import HeadAgent
    from ..agent.controller import Command, Controller
    from ..playground import Playground


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
        print_rewards: bool = True,
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

        self._playground.window.set_size(*self._size)
        self._playground.window.set_visible(True)

        self._agent = agent

        self._agent_commands: Dict[Controller, Command] = {}
        self.print_rewards = print_rewards

        self._playground.window.on_draw = self.on_draw
        self._playground.window.on_update = self.on_update
        self._playground.window.on_key_press = self.on_key_press
        self._playground.window.on_key_release = self.on_key_release

    def run(self):
        self._playground.window.run()

    def on_draw(self):

        self.update()
        self._fbo.use()

    def on_update(self, _):

        commands = self.commands
        self._playground.step(commands=commands)

        if self.print_rewards:

            for agent in self._playground.agents:
                if agent.reward != 0:
                    print(agent.reward)

    @property
    def commands(self):
        return {self._agent: self._agent_commands}

    def update(self, force=False):

        self.update_sprites(force)

        self._playground.window.use()

        self._playground.window.clear(self._background)

        # Change projection to match the contents

        self._transparent_sprites.draw(pixelated=True)
        self._interactive_sprites.draw(pixelated=True)
        self._visible_sprites.draw(pixelated=True)
        self._traversable_sprites.draw(pixelated=True)

    def on_key_press(self, key, modifiers):
        """Called whenever a key is pressed."""

        if key == arcade.key.UP:
            self._agent_commands[self._agent.base.forward_controller] = 0.2
        elif key == arcade.key.DOWN:
            self._agent_commands[self._agent.base.forward_controller] = -0.2

        if not modifiers & arcade.key.MOD_SHIFT:
            if key == arcade.key.LEFT:
                self._agent_commands[self._agent.base.angular_vel_controller] = 0.2
            elif key == arcade.key.RIGHT:
                self._agent_commands[self._agent.base.angular_vel_controller] = -0.2
        else:
            if key == arcade.key.LEFT:
                self._agent_commands[self._agent.head.joint_controller] = 0.1
            elif key == arcade.key.RIGHT:
                self._agent_commands[self._agent.head.joint_controller] = -0.1

        if key == arcade.key.Q:
            self._playground.window.close()

        if key == arcade.key.R:
            self._playground.reset()

        if key == arcade.key.G:
            self._agent_commands[self._agent.base.grasper_controller] = 1

    def on_key_release(self, key, modifiers):

        if key == arcade.key.UP:
            self._agent_commands[self._agent.base.forward_controller] = 0
        elif key == arcade.key.DOWN:
            self._agent_commands[self._agent.base.forward_controller] = 0
        if not modifiers & arcade.key.MOD_SHIFT:
            if key == arcade.key.LEFT:
                self._agent_commands[self._agent.base.angular_vel_controller] = 0
            elif key == arcade.key.RIGHT:
                self._agent_commands[self._agent.base.angular_vel_controller] = 0
        else:
            if key == arcade.key.LEFT:
                self._agent_commands[self._agent.head.joint_controller] = 0
            elif key == arcade.key.RIGHT:
                self._agent_commands[self._agent.head.joint_controller] = 0

        if key == arcade.key.G:
            self._agent_commands[self._agent.base.grasper_controller] = 0
