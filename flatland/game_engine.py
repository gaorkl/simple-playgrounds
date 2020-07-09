import pygame
from pygame.locals import K_q
from .utils.definitions import SensorModality, SIMULATION_STEPS
from pygame.color import THECOLORS
import numpy


class Engine:

    """
    Engine manages the interactions between agents and a playground.

    """

    def __init__(self, playground, agents, time_limit, replay=False, screen=False):

        """

        Args:
            playground (:obj: 'Playground): Playground where the agents will be placed
            agents (:obj: 'list' of :obj: 'Agent'): List of the agents which will play in the playground
            time_limit (:obj: 'int'): Total number of timesteps.
            replay (:obj: 'bool'): If True, the game will restart upon termination, until time_limit is reached.
                Default: False
            screen: If True, a pygame screen is created for display.
                Default: False

        Note:
            A pygame screen is created by default if one agent is controlled by Keyboard.

        """

        # Playground already exists
        self.playground = playground

        self.agents = agents
        for agent in self.agents:
            self.playground.add_agent(agent)

        # Rules
        self.replay_until_time_limit = replay
        self.time_limit = time_limit

        # Engine parameters
        self.inner_simulation_steps = SIMULATION_STEPS

        # Display screen
        self.need_command_display = False
        for agent in self.agents:
            if agent.controller and agent.controller.controller_type == 'keyboard':
                self.need_command_display = True

        self.Q_ready_to_press = False
        if self.need_command_display:
            self.Q_ready_to_press = True

        self.screen = None
        if self.need_command_display or screen:
            # Screen for Pygame
            self.screen = pygame.display.set_mode((self.playground.width, self.playground.length))
            self.screen.set_alpha(None)

        # Pygame Surfaces to display the environment
        self.surface_environment = pygame.Surface((self.playground.width, self.playground.length))
        self.surface_sensors = pygame.Surface((self.playground.width, self.playground.length))

        self.game_on = True
        self.episode_elapsed_time = 0
        self.total_elapsed_time = 0

    def multiple_steps(self, actions, n_steps=1):
        """
        Runs multiple steps of the game, with the same actions for the agents.

        Args:
            actions: Dictionary containing the actions for each agent.
            n_steps: Number of consecutive steps where the same actions will be applied

        """

        for stp in range(n_steps):
            self.step(actions)

    def step(self, actions):
        """
        Runs a single steps of the game, with the same actions for the agents.

        Args:
            actions: Dictionary containing the actions for each agent.

        """

        for agent in self.agents:
            agent.pre_step()
            agent.apply_actions_to_body_parts(actions[agent.name])

        for _ in range(self.inner_simulation_steps):
            self.playground.space.step(1. / self.inner_simulation_steps)

        self.playground.update_playground()

        # Termination
        if self.game_terminated():

            if self.replay_until_time_limit and self.total_elapsed_time < self.time_limit:
                self.game_reset()

            else:
                self.game_on = False

        self.total_elapsed_time += 1
        self.episode_elapsed_time += 1

    def game_reset(self):
        """
        Resets the game to its initial state.

        """
        self.episode_elapsed_time = 0

        self.playground.remove_agents()
        self.playground.reset()

        for agent in self.agents:
            self.playground.add_agent(agent)

    def game_terminated(self):
        """
        Tests whether the game came to an end, because of time limit or termination of playground.

        Returns:
            True if the game is terminated
            False if the game continues
        """

        if self.total_elapsed_time == self.time_limit or self.playground.has_reached_termination:
            return True

        if self.need_command_display:
            if not pygame.key.get_pressed()[K_q] and self.Q_ready_to_press is False:
                self.Q_ready_to_press = True

            elif pygame.key.get_pressed()[K_q] and self.Q_ready_to_press is True:
                self.Q_ready_to_press = False
                return True

        return False

    def update_surface_environment(self):
        """
        Draw all agents and entities on the surface environment.
        Additionally, draws the interaction areas.

        """

        self.surface_environment.fill(THECOLORS["black"])

        for entity in self.playground.entities:
            entity.draw(self.surface_environment, draw_interaction=True)

        for agent in self.agents:
            agent.draw(self.surface_environment)

    def update_observations(self):
        """
        Updates observations of each agent

        """
        # list all elements that are invisible to an agent
        invisible_elements = []
        for agent in self.agents:
            for sensor in agent.sensors:
                invisible_elements += sensor.invisible_elements

        # Generate surface only if an agent has visual sensor
        if any([agent.has_visual_sensor for agent in self.agents]):
            self.surface_sensors.fill(THECOLORS["black"])

            # Draw entities and agent parts that are not invisible

            for entity in self.playground.entities:
                if entity not in invisible_elements:
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

                    sensor.update_sensor(img_sensor, None, None)

                elif sensor.sensor_modality is SensorModality.GEOMETRIC:

                    sensor.update_sensor(None, self.playground.entities, self.playground.agents)

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

    def generate_topdown_image(self):
        """
        Updates the Environment Surface and convert it into an array.
        Color code follows OpenCV

        Returns:

        """

        self.update_surface_environment()

        imgdata = pygame.surfarray.array3d(self.surface_environment)
        imgdata = numpy.rot90(imgdata, 1, (1, 0))
        imgdata = imgdata[::-1, :, ::-1]

        return imgdata
