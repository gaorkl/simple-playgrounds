from __future__ import annotations

from typing import TYPE_CHECKING, Dict, Optional, Tuple

import arcade

from .view import TopDownView

if TYPE_CHECKING:
    from ..agent import Agent
    from ..agent.controller import Command, Controller
    from ..playground import Playground


class GUI(TopDownView):
    def __init__(
        self,
        playground: Playground,
        keyboard_agent: Optional[Agent] = None,
        size: Optional[Tuple[int, int]] = None,
        center: Tuple[float, float] = (0, 0),
        zoom: float = 1,
        display_uid: bool = False,
        draw_transparent: bool = True,
        draw_interactive: bool = True,
        draw_zone: bool = True,
        draw_sensors: bool = False,
        print_rewards: bool = True,
        print_messages: bool = True,
        random_agents: bool = True,
    ) -> None:
        super().__init__(
            playground,
            size,
            center,
            zoom,
            display_uid,
            draw_transparent,
            draw_interactive,
            draw_zone,
        )

        self._playground.window.set_size(*self._size)
        self._playground.window.set_visible(True)

        self._keyboard_agent = keyboard_agent
        self._random_agents = random_agents

        self._agent_commands: Dict[Controller, Command] = {}
        self._message = None

        self.print_rewards = print_rewards
        self.print_messages = print_messages

        self._playground.window.on_draw = self.on_draw
        self._playground.window.on_update = self.on_update
        self._playground.window.on_key_press = self.on_key_press
        self._playground.window.on_key_release = self.on_key_release

        self._draw_sensors = draw_sensors

    def run(self):
        self._playground.window.run()

    def on_draw(self):

        self.update()
        self._fbo.use()

    def on_update(self, _):

        commands = self._get_commands()

        self._playground.step(commands=commands, messages=self._message)

        if self.print_rewards:

            for agent in self._playground.agents:
                if agent.reward != 0:
                    print(agent.reward)

        if self.print_messages:

            for agent in self._playground.agents:
                for comm in agent.communicators:
                    for _, msg in comm.received_messages:
                        print(f"Agent {agent.name} received message {msg}")

        self._message = {}

    def _get_commands(self):

        command_dict = {}

        if self._random_agents:
            for agent in self._playground.agents:
                command_dict[agent] = agent.get_random_commands()

        if self._keyboard_agent:
            command_dict[self._keyboard_agent] = self._agent_commands

        return command_dict

    def update(self, force=False):

        self.update_sprites(force)

        self._playground.window.use()

        self._playground.window.clear(self._background)

        if self._draw_sensors:

            for agent in self._playground.agents:
                for sensor in agent.sensors:
                    sensor.draw()

        # Change projection to match the contents

        self._transparent_sprites.draw(pixelated=True)
        self._interactive_sprites.draw(pixelated=True)
        self._zone_sprites.draw(pixelated=True)
        self._visible_sprites.draw(pixelated=True)
        self._traversable_sprites.draw(pixelated=True)

    def on_key_press(self, key, modifiers):
        """Called whenever a key is pressed."""

        self._keyboard_agent_key_press(key, modifiers)

        if key == arcade.key.Q:
            self._playground.window.close()

        if key == arcade.key.R:
            self._playground.reset()

        if key == arcade.key.S:
            self._draw_sensors = not self._draw_sensors

    def on_key_release(self, key, modifiers):

        self._keyboard_agent_key_release(key, modifiers)

    def _keyboard_agent_key_press(self, key, modifiers):
        """
        Implement for your agent
        """

    def _keyboard_agent_key_release(self, key, modifiers):
        """
        Implement for your agent
        """


class HeadAgentGUI(GUI):
    def _keyboard_agent_key_press(self, key, modifiers):

        if key == arcade.key.UP:
            self._agent_commands["forward"] = 0.2
        elif key == arcade.key.DOWN:
            self._agent_commands["forward"] = -0.2

        if not modifiers & arcade.key.MOD_SHIFT:
            if key == arcade.key.LEFT:
                self._agent_commands["angular"] = 0.2
            elif key == arcade.key.RIGHT:
                self._agent_commands["angular"] = -0.2
        else:
            if key == arcade.key.LEFT:
                self._agent_commands["head"] = 0.1
            elif key == arcade.key.RIGHT:
                self._agent_commands["head"] = -0.1

        if key == arcade.key.M:
            self._message = {
                self._keyboard_agent: {
                    self._keyboard_agent.comm: (
                        None,
                        f"Currently at timestep {self._playground.timestep}",
                    )
                }
            }
            print(f"Agent {self._keyboard_agent.name} sends message")

        if key == arcade.key.G:
            self._agent_commands["grasper"] = 1

    def _keyboard_agent_key_release(self, key, modifiers):

        if key == arcade.key.UP:
            self._agent_commands["forward"] = 0
        elif key == arcade.key.DOWN:
            self._agent_commands["forward"] = 0
        if not modifiers & arcade.key.MOD_SHIFT:
            if key == arcade.key.LEFT:
                self._agent_commands["angular"] = 0
            elif key == arcade.key.RIGHT:

                self._agent_commands["angular"] = 0
        else:
            if key == arcade.key.LEFT:
                self._agent_commands["head"] = 0
            elif key == arcade.key.RIGHT:
                self._agent_commands["head"] = 0

        if key == arcade.key.G:
            self._agent_commands["grasper"] = 0
