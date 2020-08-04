"""
Game Engine manages the interacitons between agents and Playgrounds.
"""
import math
import numpy

import pygame
from pygame.locals import K_q, K_r  # pylint: disable=no-name-in-module
from pygame.color import THECOLORS  # pylint: disable=no-name-in-module

from simple_playgrounds.utils.definitions import SensorModality, SIMULATION_STEPS, ActionTypes
from simple_playgrounds.entities.agents.agent import Agent

class Engine:

    """
    Engine manages the interactions between agents and a playground.

    """

    # pylint: disable=too-many-function-args
    # pylint: disable=too-many-arguments
    # pylint: disable=too-many-instance-attributes

    def __init__(self, playground, time_limit=None, replay=False, screen=False):

        """

        Args:
            playground (:obj: 'Playground): Playground where the agents will be placed
            time_limit (:obj: 'int'): Total number of timesteps.
            replay (:obj: 'bool'): Restarts upon termination, until time_limit is reached.
                Default: False
            screen: If True, a pygame screen is created for display.
                Default: False

        Note:
            A pygame screen is created by default if one agent is controlled by Keyboard.
            You can reset the game by using R key, and terminate it using Q key.

        """

        # Playground already exists
        self.playground = playground

        self.agents = self.playground.agents

        # Rules
        self.replay_until_time_limit = replay

        self.time_limit = time_limit
        if time_limit is None:
            self.time_limit = self.playground.time_limit

        assert isinstance(self.time_limit, int)

        # Display screen

        self.screen = None
        if screen:
            # Screen for Pygame
            self.screen = pygame.display.set_mode((self.playground.width, self.playground.length))
            self.screen.set_alpha(None)
            self.quit_key_ready = True
            self.reset_key_ready = True


        # Pygame Surfaces to display the environment
        self.surface_environment = pygame.Surface((self.playground.width, self.playground.length))
        self.surface_sensors = pygame.Surface((self.playground.width, self.playground.length))

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

        for agent_name, agent_actions in actions.items():
            hold_actions[agent_name] = {}
            last_action[agent_name] = {}

            for part_name, part_actions in agent_actions.items():

                hold_actions[agent_name][part_name] = {}
                last_action[agent_name][part_name] = {}

                for act, val in part_actions.items():

                    if act in [ActionTypes.ACTIVATE, ActionTypes.EAT]:
                        hold_actions[agent_name][part_name][act] = 0
                        last_action[agent_name][part_name][act] = val

                    else:
                        hold_actions[agent_name][part_name][act] = val
                        last_action[agent_name][part_name][act] = val

        cumulated_rewards = {}
        for agent_name in actions:
            cumulated_rewards[agent_name] = 0

        step = 0
        continue_actions = True

        while step < n_steps and continue_actions:

            if step < n_steps-1:
                action = hold_actions
            else:
                action = last_action

            self._engine_step(action)

            for agent in self.agents:
                cumulated_rewards[agent.name] += agent.reward

            step += 1

            reset, terminate = self._handle_terminations()

            if reset or terminate:
                continue_actions = False

        for agent in self.agents:
            agent.reward = cumulated_rewards[agent.name]

        if self._reached_time_limit() and self.playground.time_limit_reached_reward is not None:
            for agent in self.agents:
                agent.reward += self.playground.time_limit_reached_reward

        return reset, terminate

    def step(self, actions):
        """
        Runs a single steps of the game, with the same actions for the agents.

        Args:
            actions: Dictionary containing the actions for each agent.

        """

        self._engine_step(actions)

        # Termination
        reset, terminate = self._handle_terminations()

        if self._reached_time_limit() and self.playground.time_limit_reached_reward is not None:
            for agent in self.agents:
                agent.reward += self.playground.time_limit_reached_reward

        return reset, terminate

    def _handle_terminations(self):

        reset = False
        terminate = False

        playground_terminated = self.playground.done
        reached_time_limit = self._reached_time_limit()
        keyboard_reset, keyboard_quit = self._check_keyboard()

        if keyboard_quit:
            terminate = True

        elif keyboard_reset:
            reset = True

        elif playground_terminated:

            if self.replay_until_time_limit:
                reset = True

            else:
                terminate = True

        elif reached_time_limit:
            terminate = True

        return reset, terminate

    def _engine_step(self, actions):

        for agent in self.agents:
            agent.apply_actions_to_body_parts(actions[agent.name])

        self.playground.update(SIMULATION_STEPS)

        self.elapsed_time += 1

    def reset(self):
        """
        Resets the game to its initial state.

        """
        self.playground.reset()
        self.game_on = True

    def _reached_time_limit(self):
        if self.elapsed_time >= self.time_limit:
            return True
        else:
            return False


    def _check_keyboard(self):
        """
        Tests whether the game came to an end, because of time limit or termination of playground.

        Returns:
            True if the game is terminated
            False if the game continues
        """
        reset_game = False
        terminate_game = False

        if self.screen is not None:

            pygame.event.get()

            # Press Q to terminate
            if pygame.key.get_pressed()[K_q] and self.quit_key_ready is False:
                self.quit_key_ready = True

            elif pygame.key.get_pressed()[K_q] and self.quit_key_ready is True:
                self.quit_key_ready = False

                terminate_game = True

            # Press R to reset
            if pygame.key.get_pressed()[K_r] and self.reset_key_ready is False:
                self.reset_key_ready = True

            elif pygame.key.get_pressed()[K_r] and self.reset_key_ready is True:
                self.reset_key_ready = False

                reset_game = True

        return reset_game, terminate_game

    def update_surface_environment(self):
        """
        Draw all agents and entities on the surface environment.
        Additionally, draws the interaction areas.

        """

        self.surface_environment.fill(THECOLORS["black"])

        for entity in self.playground.scene_elements:
            entity.draw(self.surface_environment, draw_interaction=True)

        for agent in self.agents:
            agent.draw(self.surface_environment)

    def update_observations(self):
        """
        Updates observations of each agent

        """
        # list all elements that are invisible to an agent
        invisible_elements = [inv_elem for agent in self.agents for sensor in agent.sensors
                              for inv_elem in sensor.invisible_elements]

        # Generate surface only if an agent has visual sensor
        if any([agent.has_visual_sensor for agent in self.agents]):
            self.surface_sensors.fill(THECOLORS["black"])

            # Draw entities and agent parts that are not invisible

            for entity in [ent for ent in self.playground.scene_elements
                           if ent not in invisible_elements]:
                entity.draw(self.surface_sensors, draw_interaction=False)

            for agent in self.playground.agents:
                agent.draw(self.surface_sensors, excluded=invisible_elements)

        for agent in self.agents:

            for sensor in agent.sensors:

                if sensor.sensor_modality is SensorModality.VISUAL:

                    surface_sensor = self.surface_sensors.copy()

                    # Draw elements that are not invisible to this agent
                    for element in invisible_elements:
                        if element not in sensor.invisible_elements:
                            element.draw(surface_sensor)

                    img_sensor = pygame.surfarray.array3d(surface_sensor)
                    img_sensor = numpy.rot90(img_sensor, 1, (1, 0))
                    img_sensor = img_sensor[::-1, :, ::-1]

                    sensor.update_sensor(img_sensor)

                elif sensor.sensor_modality is SensorModality.SEMANTIC:

                    sensor.update_sensor(self.playground)

                else:
                    raise ValueError

    def display_full_scene(self):
        """
        If the screen is set, updates the screen and displays the environment.

        """

        if self.screen is not None:

            self.update_surface_environment()

            rot_surface = pygame.transform.rotate(self.surface_environment, 180)
            self.screen.blit(rot_surface, (0, 0), None)

            pygame.display.flip()

        else:
            raise ValueError

    def generate_topdown_image(self, mode=None):
        """
        Updates the Environment Surface and convert it into an array.
        Color code follows OpenCV

        Returns:

        """

        self.update_surface_environment()

        imgdata = pygame.surfarray.array3d(self.surface_environment)
        imgdata = numpy.rot90(imgdata, 1, (1, 0))
        imgdata = imgdata[::-1, :, ::-1]

        if mode == 'plt':
            imgdata = imgdata[:, :, ::-1]

        return imgdata

    def generate_sensor_image(self, agent, width_sensor=200, height_sensor=30, mode = None):
        """
        Generate a full image contaning all the sensor representations of an Agent.
        Args:
            agent: Agent
            width_display: width of the display for drawing.
            height_sensor: when applicable (1D sensor), the height of the display.


        Returns:

        """

        border = 5

        list_sensor_images = [sensor.draw(width_sensor, height_sensor) for sensor in agent.sensors]

        full_height = sum([im.shape[0] for im in list_sensor_images]) + len(list_sensor_images)*(border+1)

        full_img = numpy.ones((full_height, width_sensor, 3)) * 0.2

        current_height = 0
        for im in list_sensor_images:
            current_height += border
            full_img[current_height:im.shape[0] + current_height, :, :] = im[:, :, :]
            current_height += im.shape[0]

        if mode == 'plt':
            full_img = full_img[:, :, ::-1]

        return full_img

    def run(self, steps=None, with_screen = False, print_rewards = False):
        """ Run the engine for the full duration of the game"""

        continue_for_n_steps = True

        while self.game_on and continue_for_n_steps:

            actions = {}
            for agent in self.agents:
                actions[agent.name] = agent.controller.generate_actions()

            reset, terminate = self.step(actions)
            self.update_observations()

            if with_screen and self.game_on:
                self.display_full_scene()
                pygame.time.wait(30)

            if print_rewards:
                for agent in self.agents:
                    if agent.reward != 0:
                        print(agent.name, ' got reward ', agent.reward)

            if steps is not None:
                steps -= 1
                if steps ==0:
                    continue_for_n_steps = False

            if reset:
                self.reset()

            if terminate:
                continue_for_n_steps = False
                self.terminate()


    def terminate(self):

        self.game_on = False
        pygame.quit()