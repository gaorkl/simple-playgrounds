"""
Game Engine manages the interacitons between agents and Playgrounds.
"""
import numpy as np

import pygame
from pygame.locals import K_q  # pylint: disable=no-name-in-module
from pygame.color import THECOLORS  # pylint: disable=no-name-in-module

import cv2

from simple_playgrounds.utils.definitions import SensorModality, SIMULATION_STEPS, ActionTypes


class Engine:

    """
    Engine manages the interactions between agents and a playground.

    """

    # pylint: disable=too-many-function-args
    # pylint: disable=too-many-arguments
    # pylint: disable=too-many-instance-attributes

    def __init__(self, playground, time_limit=None, screen=False):

        """

        Args:
            playground (:obj: 'Playground): Playground where the agents will be placed
            time_limit (:obj: 'int'): Total number of timesteps. Can also be defined in playground
            screen: If True, a pygame screen is created for display.
                Default: False

        Note:
            A pygame screen is created by default if one agent is controlled by Keyboard.
            You can reset the game by using R key, and terminate it using Q key.
            Screen is intended for debugging or playing by a human (using Keyboard).

            If time limit is defined in playground and engine, engine prevails.

        """

        # Playground already exists
        self.playground = playground

        self.agents = self.playground.agents

        if time_limit is not None:
            self.time_limit = time_limit

        elif self.playground.time_limit is not None:
            self.time_limit = self.playground.time_limit

        else:
            raise ValueError('Time limit should be defined in the playground or game engine')

        # Display screen

        self.screen = None
        if screen:
            # Screen for Pygame
            self.screen = pygame.display.set_mode((self.playground.width, self.playground.length))
            self.screen.set_alpha(None)
            self.quit_key_ready = True

        # Pygame Surfaces to display the environment
        self.surface_background = pygame.Surface((self.playground.width, self.playground.length))
        self.surface_environment = pygame.Surface((self.playground.width, self.playground.length))
        self.surface_sensors = pygame.Surface((self.playground.width, self.playground.length))

        self.surface_background.fill(THECOLORS["black"])

        for elem in self.playground.scene_elements:
            if elem.background:
                elem.draw(self.surface_background, )

        self.game_on = True
        self.elapsed_time = 0

    def multiple_steps(self, actions, n_steps=1):
        """
        Runs multiple steps of the game, with the same actions for the agents.
        Perforns Interactive (eat and activate) actions oly at the last timestep.

        Args:
            actions: Dictionary containing the actions for each agent.
            n_steps: Number of consecutive steps where the same actions will be applied

        """
        hold_actions = {}
        last_action = {}

        terminate = False

        for agent_name, agent_actions in actions.items():
            hold_actions[agent_name] = {}
            last_action[agent_name] = {}

            for actuator, value in agent_actions.items():

                last_action[agent_name][actuator] = value
                hold_actions[agent_name][actuator] = value

                if actuator.action in [ActionTypes.ACTIVATE, ActionTypes.EAT]:
                    hold_actions[agent_name][actuator] = 0

        cumulated_rewards = {}
        for agent in actions:
            cumulated_rewards[agent] = 0

        step = 0

        while step < n_steps and not terminate:

            if step < n_steps-1:
                action = hold_actions
            else:
                action = last_action

            self._engine_step(action)

            for agent in self.agents:
                cumulated_rewards[agent] += agent.reward

            step += 1

            terminate = self._has_terminated()

        for agent in self.agents:
            agent.reward = cumulated_rewards[agent]

        if self._reached_time_limit() and self.playground.time_limit_reached_reward is not None:
            for agent in self.agents:
                agent.reward += self.playground.time_limit_reached_reward

        return terminate

    def step(self, actions):
        """
        Runs a single steps of the game, with the same actions for the agents.

        Args:
            actions: Dictionary containing the actions for each agent. keys are agents, values are dictionary of actions.

        """

        self._engine_step(actions)

        # Termination
        terminate = self._has_terminated()

        if self._reached_time_limit() and self.playground.time_limit_reached_reward is not None:
            for agent in self.agents:
                agent.reward += self.playground.time_limit_reached_reward

        return terminate

    def _engine_step(self, actions):

        for agent in actions:
            agent.apply_actions_to_body_parts(actions[agent])

        self.playground.update(SIMULATION_STEPS)

        self.elapsed_time += 1

    def _has_terminated(self):

        playground_terminated = self.playground.done
        reached_time_limit = self._reached_time_limit()
        keyboard_quit = self._check_keyboard()

        if keyboard_quit or playground_terminated or reached_time_limit:
            self.game_on = False
            return True

        return False

    def reset(self):
        """
        Resets the game to its initial state.

        """
        self.playground.reset()
        self.elapsed_time = 0
        self.game_on = True

    def _reached_time_limit(self):
        if self.elapsed_time >= self.time_limit-1:
            return True
        return False

    def _check_keyboard(self):
        """
        Tests whether the game came to an end, because of time limit or termination of playground.

        Returns:
            True if the game is terminated
            False if the game continues
        """
        terminate_game = False

        if self.screen is not None:

            pygame.event.get()

            # Press Q to terminate
            if not pygame.key.get_pressed()[K_q] and self.quit_key_ready is False:
                self.quit_key_ready = True

            elif pygame.key.get_pressed()[K_q] and self.quit_key_ready is True:
                self.quit_key_ready = False
                terminate_game = True

        return terminate_game

    def _update_surface_background(self):
        # Check that some background elements maybe need to be drawn
        for element in self.playground.scene_elements:
            if element.background and not element.drawn:
                element.draw(self.surface_background, )

    def _update_surface_environment(self):
        """
        Draw all agents and entities on the surface environment.
        Additionally, draws the interaction areas.

        """
        self._update_surface_background()
        self.surface_environment.blit(self.surface_background, (0, 0))

        for entity in self.playground.scene_elements:

            if not entity.background or entity.graspable or entity.interactive :
                entity.draw(self.surface_environment, )

        for agent in self.agents:
            agent.draw(self.surface_environment, )

    def update_observations(self):
        """
        Updates observations of each agent

        """

        for agent in self.agents:

            for sensor in agent.sensors:

                if sensor.sensor_modality is SensorModality.VISUAL:

                    self._update_surface_background()
                    self.surface_sensors.blit(self.surface_background, (0, 0))
                    sensor.update(playground=self.playground, sensor_surface=self.surface_sensors)

                elif sensor.sensor_modality is SensorModality.ROBOTIC \
                        or sensor.sensor_modality is SensorModality.SEMANTIC:
                    sensor.update(playground=self.playground)

                else:
                    raise ValueError

    def update_screen(self):
        """
        If the screen is set, updates the screen and displays the environment.

        """

        if self.screen is not None:

            self._update_surface_environment()

            rot_surface = pygame.transform.rotate(self.surface_environment, 180)
            self.screen.blit(rot_surface, (0, 0), None)

            pygame.display.flip()

        else:
            raise ValueError('No screen to update')

    def generate_playground_image(self, max_size=None, plt_mode=False):
        """
        Updates the Environment Surface and convert it into an array.
        Color code follows OpenCV.

        For displaying with matplotlib, use plt_mode = True

        Returns: image of he playground

        """

        self._update_surface_environment()

        np_image = pygame.surfarray.pixels3d(self.surface_environment.copy())/255.
        np_image = np.rot90(np_image, 1, (1, 0))
        np_image = np_image[::-1, :, ::-1]

        if max_size is not None:

            scaling_factor = max_size/max(np_image.shape[0], np_image.shape[1])
            np_image = cv2.resize(np_image, None, fx = scaling_factor, fy = scaling_factor)

        if plt_mode:
            np_image = np_image[:, :, ::-1]

        return np_image

    def generate_agent_image(self, agent,
                             with_pg=True, max_size_pg=200, rotate_pg=False,
                             with_actions=True, width_action=200, height_action=20,
                             with_sensors=True, width_sensors=150, height_sensor=20, plt_mode=False,
                             layout=('playground', ('sensors', 'actions'))):
        """
        Method to generate an image for displaying the playground, agent sensors and actions.

        Args:
            agent (Agent): Instance of agent.
            with_pg (bool): Display the playground.
            max_size_pg (int): Maximum size of the playground image ( either width or depth, depending on shape).
            rotate_pg (bool): Rotate the playground. Useful when the playground is a rectange.
            with_actions (bool): Display actions.
            width_action (int): Width of the action bars.
            height_action (int): Height of the action bars.
            with_sensors (bool): Display sensors.
            width_sensors (int): Width of the sensors.
            height_sensor (int): Height of the sensors (when applicable).
            plt_mode (bool): Set to True to return a matplotlib compatible image.
            layout (tuple): See notes

        Note:
            Layout is a tuple representing the layout of the agent image:

            - ('playground', ('sensors', 'actions') ) will put playground on the left, then split sensors and actions
            horizontally on the right.
            - (('playground', 'sensors'), 'actions') ) will split playground and sensor on the left,
            then display sensors on the right.

        Returns:
            if plt_mode is False: returns a cv2 compatible image / array, scaled between 0 and 1.
            if plt_mode is True: returns a matplotlib compatible image / array, scaled between 0 and 1.


        """
        border = 10
        images = {}

        if with_pg:
            pg_image = self.generate_playground_image(max_size=max_size_pg)

            if rotate_pg:
                pg_image = np.rot90(pg_image)
            images['playground']=pg_image

        if with_actions:
            action_image = agent.generate_actions_image(width_action=width_action, height_action=height_action)
            images['actions'] = action_image

        if with_sensors:
            sensor_image = agent.generate_sensor_image(width_sensor=width_sensors, height_sensor=height_sensor)
            images['sensors'] = sensor_image

        full_width = border
        full_height = 0

        for column in layout:

            if isinstance(column, str):
                full_width += images[column].shape[1] + border
                full_height = max(full_height, images[column].shape[0] + 2*border)

            elif isinstance(column, tuple):
                full_width += max( [ images[col].shape[1] for col in column]) + border
                full_height = max( full_height, border + sum( images[col].shape[0] + border for col in column) )

        full_img = np.ones((full_height, full_width, 3))

        current_width = border

        for column in layout:

            if isinstance(column, str):
                full_img[border: border + images[column].shape[0],
                         current_width:current_width + images[column].shape[1], :] \
                         = images[column][:, :, :]

                current_width += images[column].shape[1] + border

            elif isinstance(column, tuple):

                current_height = border

                for col in column:

                    # center
                    delta_width = max( [ images[col].shape[1] for col in column]) - images[col].shape[1]
                    delta_width = int(delta_width/2)

                    full_img[current_height: current_height + images[col].shape[0],
                    current_width+ delta_width:current_width +delta_width+ images[col].shape[1], :] \
                        = images[col][:, :, :]

                    current_height += images[col].shape[0] + border

                current_width += max( [ images[col].shape[1] for col in column]) + border

        if plt_mode:
            full_img = full_img[:, :, ::-1]

        return full_img

    def run(self, steps=None, update_screen=False, print_rewards=False):
        """ Run the engine for the full duration of the game or a certain number of steps"""

        if self.screen is False and update_screen:
            raise ValueError("Can't update non-existing screen" )

        continue_for_n_steps = True

        while self.game_on and continue_for_n_steps:

            actions = {}
            for agent in self.agents:
                actions[agent] = agent.controller.generate_commands()

            terminate = self.step(actions)
            self.update_observations()

            if update_screen and self.game_on:
                self.update_screen()
                pygame.time.wait(30)

            if print_rewards:
                for agent in self.agents:
                    if agent.reward != 0:
                        print(agent.name, ' got reward ', agent.reward)

            if steps is not None:
                steps -= 1
                if steps == 0:
                    continue_for_n_steps = False

            if terminate:
                self.game_on = False

    def __del__(self):
        pygame.quit()


